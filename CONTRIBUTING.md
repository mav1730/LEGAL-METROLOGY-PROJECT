# Contributing (Legal Metrology Checker)

Documentation and repo-hygiene contributions are welcome. Feature and UI work should land on separate branches from docs-only PRs.

## Branching

- Default branch: `main`
- Docs / `.gitignore` / junk cleanup: `docs/…` or `chore/…`
- Product code: `feat/…` / `fix/…`
- Open a PR; leave merge decisions to the maintainer unless already agreed

## Local smoke before a docs PR

You do not need a full D: drive setup. From a clean checkout:

```bash
cd backend && python -m venv .venv && source .venv/bin/activate  # or Windows Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
# other terminal:
cd frontend && npm install && npm run dev
```

## Secrets and local paths

- Never commit `.env`, SQLite DBs under `backend/data/`, uploads, or report outputs
- Do not hard-code personal absolute paths (`C:\Users\…`, machine-only drives) in README or scripts that others must run — keep helpers optional and document relative defaults
- Rotate any key that was ever committed; do not paste secret values into issues

## Commit style

Imperative subjects: `docs: portable quick start`, `chore: drop tree.txt`.
