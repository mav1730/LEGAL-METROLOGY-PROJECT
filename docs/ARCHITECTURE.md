# Architecture — Legal Metrology Checker

Runtime map of the shipped MVP. Product intent and academic framing live in [PROJECT_SPEC.md](./PROJECT_SPEC.md).

## Intent

First-pass **screening** of e-commerce listing / packaging text for Legal Metrology–style fields. Humans confirm findings. The system must not invent missing fields or act as a legal authority.

## High-level flow

```
Client (React / Vite dashboard)
  → Flask API (/api/*)
       → ingest (URL scrape | image OCR | pasted text | demo sample)
       → field_extractor (regex, precision-first)
       → rule engine (data/rules.json)
       → storage (SQLite)
       → review + report (JSON / PDF)
```

DemoMart (`/demo/…`) is a **fake store** served by the backend so viva demos do not depend on live marketplaces.

## Layers

| Path | Role |
|------|------|
| `frontend/` | Regulator-style dashboard; Vite proxies `/api` to Flask |
| `backend/app/routes/` | HTTP surface |
| `backend/app/field_extractor/` | Presence / ambiguity-aware extraction |
| `backend/app/services/` | Scraper, OCR, rules, pipeline, reports, storage |
| `backend/data/` | Rules JSON, SQLite DB, uploads, reports (DB/uploads/reports gitignored) |
| `backend/tests/` | Pytest suite |

## Configuration

`backend/.env.example` documents:

- `FLASK_ENV`, `SECRET_KEY`, `DATA_DIR`, `HOST`, `PORT`
- `DEMO_MODE=1` — prefer sample responses when live scrape/OCR fails

Optional Playwright browsers may live outside the repo via `PLAYWRIGHT_BROWSERS_PATH`. Root `start-backend.ps1` optionally delegates to a machine-local D: helper **if present**, otherwise runs `backend/run.py` with system/venv Python.

## Non-goals (current tree)

- No paid LLM required for field extraction
- No claim of legal certification from the score
- Live scrape quality is best-effort; demos must work offline via samples / DemoMart

## Related

- [README.md](../README.md) — portable quick start + API table
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR and secrets hygiene
- [PROJECT_SPEC.md](./PROJECT_SPEC.md) — full specification
