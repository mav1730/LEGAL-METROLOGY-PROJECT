# AI-Based Automated Legal Metrology & E-Commerce Compliance Checker

**Mini project (SIES GST · Computer Engineering · Idea Presentation 2026–27)**  
Decision-support web app that screens e-commerce product listings / packaging for **potential** missing Legal Metrology–style declarations.

> **Not a legal authority.** Automated findings are first-pass screening only. A human reviewer must confirm before any enforcement conclusion.

---

## What it does

1. Accept **product URL**, **packaging image**, **pasted text**, or **demo samples**
2. Collect page text (scraper) and/or OCR text (optional free Tesseract)
3. **Precision-first field extraction** (MRP, net qty, manufacturer, origin, dates…)
4. Run a **configurable rule engine** (presence / any-of / ambiguous)
5. Show **evidence + confidence** on a regulator-style dashboard
6. Support **human review** (confirm / reject / needs review)
7. Generate **JSON / PDF reports**

---

## Stack (MVP)

| Layer | Choice | Notes |
|-------|--------|--------|
| Frontend | React + Vite | Dashboard UI |
| Backend | Flask | APIs + orchestration |
| DB | SQLite | Free, zero-setup |
| Field extract | Pure Python regex | No paid AI required |
| OCR | Tesseract (optional) | Free; samples/text work without it |
| Scraper | requests + BeautifulSoup | Best-effort; demos use samples |
| Optional browser | Playwright | Richer marketplace pages when installed |

---

## Quick start (portable)

Works from the repo root on any machine with Python 3.10+ and Node 20+. Paths below are **relative** — no hard-coded drive letters.

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows; or: cp .env.example .env
python run.py
```

Or from the repo root on Windows (falls back to system Python if a local D: helper is absent):

```powershell
.\start-backend.ps1
```

| Endpoint | URL |
|----------|-----|
| API | http://127.0.0.1:5000 |
| Health | http://127.0.0.1:5000/api/health |
| DemoMart | http://127.0.0.1:5000/demo/ |

Optional: if you keep Playwright browsers or a venv outside the repo (e.g. a large disk), point `PLAYWRIGHT_BROWSERS_PATH` / your own helper scripts there. The checked-in `start-backend.ps1` will use `D:\legal-metrology\scripts\start-backend.ps1` **only when that file exists**.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 — Vite proxies `/api` → Flask.

Windows helper from repo root: `.\start-frontend.ps1`

### 3. Tests

```bash
cd backend
pip install pytest
pytest -q
```

---

## DemoMart (fake store for viva / demos)

Full product pages with images, prices, specs, and Legal Metrology text:

| Store | URL |
|-------|-----|
| Home | http://127.0.0.1:5000/demo/ |
| Honey (complete) | http://127.0.0.1:5000/demo/dp/hive-organic-honey-500g |
| Oil (missing origin) | http://127.0.0.1:5000/demo/dp/pure-groundnut-oil-1l |
| Chips (sparse) | http://127.0.0.1:5000/demo/dp/crunchyco-spicy-chips-50g |
| Tea (complete) | http://127.0.0.1:5000/demo/dp/assam-classic-tea-bags-100g |

**Test flow:** open product page → copy URL → Compliance Dashboard → **Product URL** → Scan.

### Demo path (recommended for viva)

1. Open DemoMart: http://127.0.0.1:5000/demo/
2. Open dashboard: http://127.0.0.1:5173/
3. Scan honey product URL → score ~100
4. Scan oil product URL → country of origin missing
5. Scan chips product URL → multiple missing fields
6. Confirm/reject findings → Generate PDF report

---

## API overview

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health + OCR availability |
| GET | `/api/stats` | Dashboard metrics |
| GET | `/api/samples` | Demo sample list |
| GET | `/api/rules` | Configured rule set |
| POST | `/api/scan/sample` | `{ "sample_id": "honey_complete" }` |
| POST | `/api/scan/text` | `{ "page_text", "ocr_text", "name?" }` |
| POST | `/api/scan/url` | `{ "url" }` |
| POST | `/api/scan/image` | multipart `image` |
| GET | `/api/products` | List scans |
| GET | `/api/products/:id` | Detail + fields + findings |
| POST | `/api/findings/:id/review` | `{ "action": "confirm\|reject\|needs_review", "comment?" }` |
| POST | `/api/products/:id/review` | Product-level review status |
| POST | `/api/products/:id/report` | `{ "format": "json\|pdf" }` |

---

## Design principles

- **Never invent fields** — missing → `not_detected` with reason
- **Conflicts → `ambiguous`** — human review, no silent pick
- **Bare prices ≠ MRP** without an MRP label
- **Score is prioritization only**, not certification
- **Disclaimer on every API response / report**
- Live marketplace scrape is best-effort; demos must not depend on it

---

## Project layout

```
LEGAL-METROLOGY-PROJECT/
  backend/
    app/
      field_extractor/
      services/          # scraper, ocr, rules, pipeline, reports, storage
      routes/
      main.py
    data/rules.json
    tests/
    run.py
    .env.example
  frontend/
    src/
  docs/
    PROJECT_SPEC.md
    ARCHITECTURE.md
  README.md
  CONTRIBUTING.md
  start-backend.ps1
  start-frontend.ps1
```

---

## Optional: Tesseract OCR

1. Install [Tesseract](https://github.com/tesseract-ocr/tesseract)
2. `pip install pytesseract pillow`
3. Restart backend — health shows `ocr_tesseract_available: true`

---

## Docs map

| Doc | Purpose |
|-----|---------|
| [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) | Academic / product specification |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Runtime shape and boundaries |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branches, secrets, PR hygiene |

---

## SDG alignment

- **SDG 9** — digital inspection infrastructure
- **SDG 12** — clearer product information
- **SDG 16** — transparent regulatory screening workflows

---

## Team / academic context

Built as a complete mini-project prototype from the detailed concept document
*AI-Based Automated Legal Metrology & E-Commerce Compliance Checker*.
