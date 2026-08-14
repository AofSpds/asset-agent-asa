# Semiconductor Research Control Plane

Private repository for the **반도체 연구** project control plane.

## Repository role

This repository stores versioned, reviewable control-plane artifacts such as architecture contracts, schema contracts, migration manifests, protocol definitions, hashes, release metadata, and lightweight bootstrap/index files.

Large binary/raw analytical data (for example yearly `marcap-*.parquet`) is **not** canonicalized in Git. Git stores its dataset identity, hash, and stable storage locator; raw bytes belong in the external data plane.

## Current materialization status

- `SEMI-SCHEMA-REGISTRY v0.1` — **FROZEN baseline**
  - Approved frozen ZIP SHA-256: `57916b73d86de7bef0f22ed5d733a32a70e726c1bffed6499503afb0ea57ccf6`
  - The 14 YAML contracts are materialized under `control/schemas/v0.1/`.
- `SEMI-ARCHITECTURE-SPEC v1.0` — logically **FROZEN / ACTIVE**, but its exact standalone artifact/hash must be materialized before repository activation is declared complete.
- Migration Package v1.0 — **FROZEN logically**; exact final standalone artifacts/hashes are pending repository materialization.
- Canonical data cutover — **NOT PERFORMED**.
- U127 working research — **STAGING / IN PROGRESS**, not canonical truth.

## Core policy

`WORKING → STAGING → FROZEN → ACTIVE`

Frozen artifacts are never silently overwritten. Changes are introduced through a new version/change request, validated, frozen, then promoted by manifest pointer update.

Generated views and reports are not canonical truth.
