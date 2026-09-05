from pathlib import Path
import argparse
import base64
import hashlib
import io
import re
import zipfile

EXPECTED_NAME = "AAA_M3TOP3_GR_RESEARCH_PACKAGE_v0.2_WORKING.zip"
EXPECTED_SHA256 = "5bbe75a4c9966abcb9f10d2f1e84df983977c1cf76d69e7bda6dfe4f24e60836"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    text = args.packet.read_text(encoding="utf-8")
    blocks = re.findall(r"```aaa-original-zip-base64\s*\n(.*?)\n```", text, re.DOTALL)
    if len(blocks) != 1:
        raise ValueError("Expected exactly one embedded ZIP block")
    payload = base64.b64decode("".join(blocks[0].split()), validate=True)
    if len(payload) != 40210 or hashlib.sha256(payload).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Embedded ZIP length/SHA-256 mismatch")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if len(archive.infolist()) != 10 or archive.testzip() is not None:
            raise ValueError("ZIP directory/CRC check failed")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    target = args.output_dir / EXPECTED_NAME
    if target.exists():
        if target.read_bytes() != payload:
            raise FileExistsError("Existing target differs; refusing to overwrite")
    else:
        with target.open("xb") as stream:
            stream.write(payload)
    print(f"ZIP_BYTES_VERIFIED: {target} | bytes={len(payload)} | SHA256={EXPECTED_SHA256}")


if __name__ == "__main__":
    main()
