#!/usr/bin/env python3
"""Read-only flat Parquet fallback for the frozen FinanceData/marcap inputs.

Supports the observed PLAIN/RLE_DICTIONARY encodings and UNCOMPRESSED/SNAPPY codecs.
It never writes Parquet and cannot materialize canonical bytes.
"""
from __future__ import annotations

from dataclasses import dataclass
import ctypes
import ctypes.util
import math
import os
import struct
from typing import Any, Iterable

import numpy as np

try:
    from thrift.Thrift import TType
    from thrift.protocol.TCompactProtocol import TCompactProtocol
    from thrift.transport.TTransport import TMemoryBuffer
except Exception as exc:
    raise RuntimeError("fallback Parquet reader requires the Python 'thrift' package") from exc

TYPE_BOOLEAN=0; TYPE_INT32=1; TYPE_INT64=2; TYPE_INT96=3; TYPE_FLOAT=4; TYPE_DOUBLE=5; TYPE_BYTE_ARRAY=6; TYPE_FIXED_LEN_BYTE_ARRAY=7
ENCODING_PLAIN=0; ENCODING_PLAIN_DICTIONARY=2; ENCODING_RLE=3; ENCODING_RLE_DICTIONARY=8
CODEC_UNCOMPRESSED=0; CODEC_SNAPPY=1
PAGE_DATA=0; PAGE_INDEX=1; PAGE_DICTIONARY=2; PAGE_DATA_V2=3

@dataclass(frozen=True)
class ColumnMeta:
    name: str
    physical_type: int
    repetition_type: int | None
    logical_type: Any
    type_length: int | None
    codec: int
    encodings: tuple[int, ...]
    num_values: int
    data_page_offset: int
    dictionary_page_offset: int | None
    total_compressed_size: int

@dataclass(frozen=True)
class ParquetMeta:
    path: str
    num_rows: int
    created_by: str | None
    columns: dict[str, ColumnMeta]
    row_group_count: int


def _read_generic(proto: TCompactProtocol, ttype: int) -> Any:
    if ttype == TType.BOOL: return proto.readBool()
    if ttype == TType.BYTE: return proto.readByte()
    if ttype == TType.I16: return proto.readI16()
    if ttype == TType.I32: return proto.readI32()
    if ttype == TType.I64: return proto.readI64()
    if ttype == TType.DOUBLE: return proto.readDouble()
    if ttype == TType.STRING:
        raw=proto.readBinary()
        try: return raw.decode("utf-8")
        except UnicodeDecodeError: return raw
    if ttype == TType.STRUCT:
        out={}; proto.readStructBegin()
        while True:
            _, field_type, field_id=proto.readFieldBegin()
            if field_type == TType.STOP: break
            out[field_id]=_read_generic(proto, field_type); proto.readFieldEnd()
        proto.readStructEnd(); return out
    if ttype == TType.LIST:
        elem_type,size=proto.readListBegin(); out=[_read_generic(proto,elem_type) for _ in range(size)]; proto.readListEnd(); return out
    if ttype == TType.SET:
        elem_type,size=proto.readSetBegin(); out=[_read_generic(proto,elem_type) for _ in range(size)]; proto.readSetEnd(); return out
    if ttype == TType.MAP:
        key_type,value_type,size=proto.readMapBegin(); out={}
        for _ in range(size): out[_read_generic(proto,key_type)]=_read_generic(proto,value_type)
        proto.readMapEnd(); return out
    raise ValueError(f"unsupported thrift type {ttype}")


def _parse_compact_struct(data: bytes):
    transport=TMemoryBuffer(data); proto=TCompactProtocol(transport)
    return _read_generic(proto,TType.STRUCT), transport._buffer.tell()


def inspect_parquet(path: str) -> ParquetMeta:
    with open(path,"rb") as handle:
        handle.seek(-8,os.SEEK_END); tail=handle.read(8)
        if len(tail)!=8 or tail[4:]!=b"PAR1": raise ValueError(f"not a Parquet file: {path}")
        footer_len=struct.unpack("<I",tail[:4])[0]; handle.seek(-8-footer_len,os.SEEK_END); footer=handle.read(footer_len)
    metadata,_=_parse_compact_struct(footer); schema=metadata[2]; row_groups=metadata[4]
    if len(row_groups)!=1: raise ValueError(f"fallback reader supports one row group; observed {len(row_groups)}")
    chunks=row_groups[0][1]
    if len(schema)-1!=len(chunks): raise ValueError("schema/column-chunk cardinality mismatch")
    columns={}
    for schema_elem,chunk in zip(schema[1:],chunks):
        md=chunk[3]; name=str(schema_elem[4])
        columns[name]=ColumnMeta(name,int(schema_elem[1]),int(schema_elem[3]) if 3 in schema_elem else None,
            schema_elem.get(10),int(schema_elem[2]) if 2 in schema_elem else None,int(md[4]),tuple(int(x) for x in md[2]),
            int(md[5]),int(md[9]),int(md[11]) if 11 in md else None,int(md[7]))
    return ParquetMeta(path,int(metadata[3]),metadata.get(6),columns,len(row_groups))

_SNAPPY=None

def _snappy_lib():
    global _SNAPPY
    if _SNAPPY is not None: return _SNAPPY
    name=ctypes.util.find_library("snappy")
    if not name: raise RuntimeError("SNAPPY codec required but libsnappy was not found")
    lib=ctypes.CDLL(name)
    lib.snappy_uncompressed_length.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]; lib.snappy_uncompressed_length.restype=ctypes.c_int
    lib.snappy_uncompress.argtypes=[ctypes.c_char_p,ctypes.c_size_t,ctypes.c_char_p,ctypes.POINTER(ctypes.c_size_t)]; lib.snappy_uncompress.restype=ctypes.c_int
    _SNAPPY=lib; return lib

def _snappy_decompress(data: bytes) -> bytes:
    lib=_snappy_lib(); out_len=ctypes.c_size_t()
    if lib.snappy_uncompressed_length(data,len(data),ctypes.byref(out_len))!=0: raise RuntimeError("snappy length failure")
    output=ctypes.create_string_buffer(out_len.value); actual=ctypes.c_size_t(out_len.value)
    if lib.snappy_uncompress(data,len(data),output,ctypes.byref(actual))!=0: raise RuntimeError("snappy decompress failure")
    return output.raw[:actual.value]

def _decompress(codec:int,data:bytes)->bytes:
    if codec==CODEC_UNCOMPRESSED: return data
    if codec==CODEC_SNAPPY: return _snappy_decompress(data)
    raise ValueError(f"unsupported Parquet codec enum={codec}")

def _read_varint(buf:bytes,pos:int):
    value=0; shift=0
    while True:
        byte=buf[pos]; pos+=1; value|=(byte&0x7F)<<shift
        if byte<0x80: return value,pos
        shift+=7
        if shift>63: raise ValueError("invalid hybrid-RLE varint")

def _bitpacked_values(chunk:bytes,bit_width:int,count:int)->np.ndarray:
    if count==0: return np.empty(0,dtype=np.int64)
    if bit_width==0: return np.zeros(count,dtype=np.int64)
    bits=np.unpackbits(np.frombuffer(chunk,dtype=np.uint8),bitorder="little")[:count*bit_width]
    matrix=bits.reshape(count,bit_width).astype(np.int64,copy=False); weights=(1<<np.arange(bit_width,dtype=np.int64))
    return matrix@weights

def _decode_hybrid(buf:bytes,bit_width:int,count:int,pos:int=0):
    pieces=[]; produced=0; byte_width=(bit_width+7)//8
    while produced<count:
        header,pos=_read_varint(buf,pos)
        if (header&1)==0:
            run=header>>1; value=0 if bit_width==0 else int.from_bytes(buf[pos:pos+byte_width],"little")
            if bit_width: pos+=byte_width
            take=min(run,count-produced); pieces.append(np.full(take,value,dtype=np.int64)); produced+=take
        else:
            groups=header>>1; total=groups*8; nbytes=groups*bit_width; chunk=buf[pos:pos+nbytes]; pos+=nbytes
            take=min(total,count-produced); pieces.append(_bitpacked_values(chunk,bit_width,total)[:take]); produced+=take
    return (np.concatenate(pieces) if pieces else np.empty(0,dtype=np.int64)),pos

def _plain_decode(buf:bytes,physical_type:int,count:int,type_length:int|None):
    if count==0: return (np.empty(0,dtype=object) if physical_type==TYPE_BYTE_ARRAY else np.empty(0)),0
    if physical_type==TYPE_DOUBLE:
        n=count*8; return np.frombuffer(buf[:n],dtype="<f8").copy(),n
    if physical_type==TYPE_FLOAT:
        n=count*4; return np.frombuffer(buf[:n],dtype="<f4").copy(),n
    if physical_type==TYPE_INT64:
        n=count*8; return np.frombuffer(buf[:n],dtype="<i8").copy(),n
    if physical_type==TYPE_INT32:
        n=count*4; return np.frombuffer(buf[:n],dtype="<i4").copy(),n
    if physical_type==TYPE_BYTE_ARRAY:
        out=np.empty(count,dtype=object); pos=0
        for i in range(count):
            length=struct.unpack_from("<I",buf,pos)[0]; pos+=4; raw=buf[pos:pos+length]; pos+=length
            try: out[i]=raw.decode("utf-8")
            except UnicodeDecodeError: out[i]=raw
        return out,pos
    if physical_type==TYPE_FIXED_LEN_BYTE_ARRAY:
        if not type_length: raise ValueError("fixed-len byte array missing type_length")
        n=count*type_length; raw=buf[:n]; out=np.empty(count,dtype=object)
        for i in range(count): out[i]=raw[i*type_length:(i+1)*type_length]
        return out,n
    raise ValueError(f"unsupported PLAIN physical type enum={physical_type}")

def _max_definition_level(meta:ColumnMeta)->int: return 1 if meta.repetition_type==1 else 0

def _decode_levels_v1(buf:bytes,max_level:int,count:int,pos:int):
    if max_level==0: return np.zeros(count,dtype=np.int8),pos
    length=struct.unpack_from("<I",buf,pos)[0]; pos+=4; section=buf[pos:pos+length]; pos+=length
    bit_width=max(1,math.ceil(math.log2(max_level+1))); values,_=_decode_hybrid(section,bit_width,count)
    return values.astype(np.int8,copy=False),pos

def _reconstruct_nullable(values:np.ndarray,levels:np.ndarray,max_level:int):
    if max_level==0 or np.all(levels==max_level): return values
    present=levels==max_level
    if values.dtype.kind=="f":
        out=np.full(levels.shape[0],np.nan,dtype=values.dtype); out[present]=values; return out
    out=np.empty(levels.shape[0],dtype=object); out[:]=None; out[present]=values.astype(object) if values.dtype.kind in "iu" else values; return out

def _read_page_header(handle,offset:int):
    handle.seek(offset); data=handle.read(65536)
    if not data: raise EOFError(f"unexpected EOF reading page header at {offset}")
    return _parse_compact_struct(data)

def read_column(path:str,meta:ColumnMeta)->np.ndarray:
    start=meta.dictionary_page_offset if meta.dictionary_page_offset is not None else meta.data_page_offset
    dictionary=None; pieces=[]; values_seen=0; offset=start; max_def=_max_definition_level(meta)
    with open(path,"rb") as handle:
        while values_seen<meta.num_values:
            header,header_len=_read_page_header(handle,offset); page_type=int(header[1]); compressed_size=int(header[3])
            handle.seek(offset+header_len); compressed=handle.read(compressed_size)
            if len(compressed)!=compressed_size: raise EOFError("truncated Parquet page")
            if page_type==PAGE_DICTIONARY:
                body=_decompress(meta.codec,compressed); page=header[7]; nvals=int(page[1]); encoding=int(page[2])
                if encoding!=ENCODING_PLAIN: raise ValueError(f"unsupported dictionary encoding={encoding}")
                dictionary,_=_plain_decode(body,meta.physical_type,nvals,meta.type_length)
            elif page_type==PAGE_DATA:
                body=_decompress(meta.codec,compressed); page=header[5]; nvals=int(page[1]); encoding=int(page[2]); pos=0
                levels,pos=_decode_levels_v1(body,max_def,nvals,pos); present_count=int(np.count_nonzero(levels==max_def)) if max_def else nvals
                if encoding in (ENCODING_RLE_DICTIONARY,ENCODING_PLAIN_DICTIONARY):
                    if dictionary is None: raise ValueError("dictionary-encoded data page without dictionary")
                    bit_width=body[pos]; pos+=1; indices,pos=_decode_hybrid(body,bit_width,present_count,pos); decoded=dictionary[indices]
                elif encoding==ENCODING_PLAIN:
                    decoded,consumed=_plain_decode(body[pos:],meta.physical_type,present_count,meta.type_length); pos+=consumed
                else: raise ValueError(f"unsupported data encoding={encoding}")
                pieces.append(_reconstruct_nullable(decoded,levels,max_def)); values_seen+=nvals
            elif page_type==PAGE_DATA_V2:
                page=header[8]; nvals=int(page[1]); num_nulls=int(page[2]); rep_len=int(page[6]); def_len=int(page[5]); is_compressed=bool(page.get(7,True))
                level_prefix=compressed[:rep_len+def_len]; value_payload=compressed[rep_len+def_len:]
                if is_compressed: value_payload=_decompress(meta.codec,value_payload)
                def_section=level_prefix[rep_len:rep_len+def_len]
                if max_def:
                    bit_width=max(1,math.ceil(math.log2(max_def+1))); levels,_=_decode_hybrid(def_section,bit_width,nvals); levels=levels.astype(np.int8,copy=False)
                else: levels=np.zeros(nvals,dtype=np.int8)
                present_count=nvals-num_nulls; encoding=int(page[4]); pos=0
                if encoding in (ENCODING_RLE_DICTIONARY,ENCODING_PLAIN_DICTIONARY):
                    if dictionary is None: raise ValueError("dictionary-encoded data page without dictionary")
                    bit_width=value_payload[pos]; pos+=1; indices,pos=_decode_hybrid(value_payload,bit_width,present_count,pos); decoded=dictionary[indices]
                elif encoding==ENCODING_PLAIN: decoded,_=_plain_decode(value_payload,meta.physical_type,present_count,meta.type_length)
                else: raise ValueError(f"unsupported data-v2 encoding={encoding}")
                pieces.append(_reconstruct_nullable(decoded,levels,max_def)); values_seen+=nvals
            elif page_type!=PAGE_INDEX: raise ValueError(f"unsupported page type={page_type}")
            offset+=header_len+compressed_size
    if values_seen!=meta.num_values: raise ValueError(f"column row count mismatch {values_seen} != {meta.num_values}")
    result=np.concatenate(pieces) if len(pieces)>1 else pieces[0]
    if len(result)!=meta.num_values: raise ValueError("decoded column length mismatch")
    return result

def timestamp_unit(logical_type:Any)->str|None:
    if not isinstance(logical_type,dict) or 8 not in logical_type: return None
    ts=logical_type[8]; unit_union=ts.get(2,{}) if isinstance(ts,dict) else {}
    if 1 in unit_union: return "ms"
    if 2 in unit_union: return "us"
    if 3 in unit_union: return "ns"
    return None

def physical_type_name(value:int)->str:
    return {TYPE_BOOLEAN:"BOOLEAN",TYPE_INT32:"INT32",TYPE_INT64:"INT64",TYPE_INT96:"INT96",TYPE_FLOAT:"FLOAT",TYPE_DOUBLE:"DOUBLE",TYPE_BYTE_ARRAY:"BYTE_ARRAY",TYPE_FIXED_LEN_BYTE_ARRAY:"FIXED_LEN_BYTE_ARRAY"}.get(value,f"UNKNOWN({value})")

def read_columns(path:str,names:Iterable[str]):
    meta=inspect_parquet(path); out={}
    for name in names:
        if name not in meta.columns: raise KeyError(f"column {name!r} not present in {path}")
        out[name]=read_column(path,meta.columns[name])
    return meta,out
