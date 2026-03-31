# Answer Engine

Pipeline-based answering module built on top of CfHEE.

## Current implementation

The repository currently includes a minimal backend scaffold under `apps/backend`:
- installable package: `answer_engine_backend`
- FastAPI application bootstrap
- unversioned `GET /health` endpoint

## Backend local run

From `apps/backend`:

```powershell
pip install -e .
python -m uvicorn answer_engine_backend.main:app --host 127.0.0.1 --port 8761 --reload
```
