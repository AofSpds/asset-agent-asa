# Asset Agent ASA — VS Code local run

Target branch: `aaa-t17-run-registry-ops-dashboard-v0`

This guide is for local engineering/shadow observation only. It does not grant canonical write, Independent Validation, release, replay, freeze, or cutover authority.

## 1. Checkout the exact engineering branch

```bash
git fetch origin
git checkout aaa-t17-run-registry-ops-dashboard-v0
git pull --ff-only origin aaa-t17-run-registry-ops-dashboard-v0
```

## 2. Python environment

Python 3.12 is the CI reference version.

PowerShell:

```powershell
$env:PYTHONPATH="aaa/src"
python -m unittest discover -s aaa/tests -p "test_*.py" -v
python -m aaa.cli --repo-root . runs --json
python -m aaa.cli --repo-root . personas --json
```

macOS/Linux:

```bash
export PYTHONPATH=aaa/src
python -m unittest discover -s aaa/tests -p 'test_*.py' -v
python -m aaa.cli --repo-root . runs --json
python -m aaa.cli --repo-root . personas --json
```

## 3. Start the read-only AAA API

PowerShell or macOS/Linux with `PYTHONPATH=aaa/src` already set:

```bash
python -m aaa.cli --repo-root . serve --host 127.0.0.1 --port 8765
```

Read-only endpoints used by the Owner Console:

- `GET /api/aaa/status`
- `GET /api/aaa/work`
- `GET /api/aaa/gates`
- `GET /api/aaa/state/compare`
- `GET /api/aaa/runs`
- `GET /api/aaa/personas`

Mutation methods remain denied.

## 4. Start the Owner Console

Open a second VS Code terminal:

```bash
cd aaa/web
npm ci
npm run dev
```

Open `http://127.0.0.1:5173` and select **Operations**.

The Operations view reads the same persistent Run Registry as the CLI/API. If evidence is absent, the UI must not fabricate a RUNNING state.

## 5. Current bootstrap evidence

- Work Order: `control/workorders/WO-AAA-RUN-REGISTRY-OPERATIONS-DASHBOARD-20260816.yaml`
- Run: `control/aaa/runs/RUN-AAA-T17-OPS-DASHBOARD-20260816-001.json`
- Result: `control/aaa/results/RESULT-AAA-T17-OPS-DASHBOARD-v0.1.json`

The bootstrap engineering Run is terminal `COMPLETED_PASS`. This is an Engineering result only, not an Independent Validation verdict.
