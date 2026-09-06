# Architecture — Legal Metrology Checker

Runtime map of the shipped MVP. Product intent and academic framing live in [PROJECT_SPEC.md](./PROJECT_SPEC.md). A generated overview also exists at the repo root: [Legal_Metrology_Project_Tech_Stack.pdf](../Legal_Metrology_Project_Tech_Stack.pdf).

## Intent

First-pass **screening** of e-commerce listing / packaging text for Legal Metrology–style fields. Humans confirm findings. The system must not invent missing fields or act as a legal authority.

## High-level flow

```
Client (React / Vite — MetroCheck AI)
  Landing | Compliance Scanner | Catalog & Scan History | Metrology Rules
  → Flask API (/api/*)
       → ingest (URL scrape | image OCR | pasted text | demo sample)
       → field_extractor (regex, precision-first)
       → rule engine (data/rules.json)
       → storage (SQLite)
       → review + report (JSON / PDF)
```

DemoMart (`/demo/…`) is a **fake store** served by the backend (`backend/app/demo_store/`) so viva demos do not depend on live marketplaces. Frontend catalog data (`frontend/src/data/demomartCatalog.js`) mirrors the same ~17 product slugs for in-app browse → scan.

## Layers

| Path | Role |
|------|------|
| `frontend/src/pages/` | Landing, ComplianceScan, CatalogHistory, Rules |
| `frontend/src/components/` | Scan panel, product detail, stats, landing hero |
| `frontend/src/data/` | DemoMart catalog + statutory rules presentation data |
| `backend/app/routes/` | HTTP `/api/*` surface |
| `backend/app/field_extractor/` | Presence / ambiguity-aware extraction |
| `backend/app/services/` | Scraper, OCR, rules, pipeline, reports, storage |
| `backend/app/demo_store/` | Catalog, HTML render, static assets for `/demo/` |
| `backend/data/` | Rules JSON, SQLite DB, uploads, reports (DB/uploads/reports gitignored) |
| `backend/tests/` | Pytest suite |

## Configuration

`backend/.env.example` documents:

- `FLASK_ENV`, `SECRET_KEY`, `DATA_DIR`, `HOST`, `PORT`
- `DEMO_MODE=1` — prefer sample responses when live scrape/OCR fails

Optional Playwright browsers may live outside the repo via `PLAYWRIGHT_BROWSERS_PATH`. Root `start-backend.ps1` optionally delegates to a machine-local D: helper **if present**, otherwise runs `backend/run.py` with system/venv Python.

## Key decisions visible in the tree

- **Precision-first regex extraction** over paid LLMs for core fields
- **SQLite** for zero-setup persistence of scans / findings / reports
- **DemoMart + samples** so demos work without marketplace access
- **Hash-based UI pages** (no React Router dependency in the current tree)
- **Human review** endpoints for findings and products before treating results as final

## Non-goals (current tree)

- No paid LLM required for field extraction
- No claim of legal certification from the score
- Live scrape quality is best-effort; demos must work offline via samples / DemoMart
- No public hosted URL is part of this architecture doc

## Related

- [README.md](../README.md) — portable quick start + API table
- [CONTRIBUTING.md](../CONTRIBUTING.md) — PR and secrets hygiene
- [PROJECT_SPEC.md](./PROJECT_SPEC.md) — full specification
