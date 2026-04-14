# Skill: run-tests

Run the full test suite for the PHX repository.

## API Tests

```bash
cd services/api
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Ingest Tests

```bash
cd services/ingest
pip install -r requirements.txt
python -m pytest tests/ -v
```

## E2E Tests (requires running stack)

```bash
E2E=1 E2E_API_URL=http://localhost:8000 python -m pytest tests/e2e/ -v
```

## All Tests (from repo root)

```bash
# API unit tests
cd services/api && python -m pytest tests/ -v && cd ../..

# Ingest unit tests
cd services/ingest && python -m pytest tests/ -v && cd ../..
```

## Test Coverage Report

```bash
cd services/api
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## What to Check

- All tests pass before any release
- Auth tests cover login, invalid password, JWT expiry
- Role tests cover every role and multi-role union
- RAG tests cover prompt building, citations, insufficient context
- Ingest tests cover scan, hash, skip unchanged
