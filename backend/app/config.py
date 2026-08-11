from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Keep heavy browser binaries on D: by default (saves C: space)
_DEFAULT_PLAYWRIGHT = Path(r"D:\legal-metrology\browsers")
if "PLAYWRIGHT_BROWSERS_PATH" not in os.environ and _DEFAULT_PLAYWRIGHT.is_dir():
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_DEFAULT_PLAYWRIGHT)

BASE_DIR = Path(__file__).resolve().parents[1]
# Runtime data (DB, uploads, reports) also prefer D: when available
_DEFAULT_DATA = Path(r"D:\legal-metrology\data")
if os.getenv("DATA_DIR"):
    DATA_DIR = Path(os.getenv("DATA_DIR")).resolve()
elif _DEFAULT_DATA.parent.is_dir():
    DATA_DIR = _DEFAULT_DATA
    DATA_DIR.mkdir(parents=True, exist_ok=True)
else:
    DATA_DIR = (BASE_DIR / "data").resolve()

UPLOAD_DIR = DATA_DIR / "uploads"
SAMPLES_DIR = DATA_DIR / "samples"
DB_PATH = DATA_DIR / "compliance.db"
# Rules stay with the app package (small file)
RULES_PATH = Path(os.getenv("RULES_PATH", BASE_DIR / "data" / "rules.json")).resolve()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "dev-legal-metrology-key")
DEMO_MODE = os.getenv("DEMO_MODE", "1") not in ("0", "false", "False")
PLAYWRIGHT_BROWSERS_PATH = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")

# Decision-support disclaimer (always returned by API)
SYSTEM_DISCLAIMER = (
    "This system is a compliance-screening and decision-support tool. "
    "Automated findings are potential issues only and are not a final legal "
    "determination. A human reviewer must confirm before any enforcement action."
)


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
