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

# Field extractor: regex (precision-first) | ner (offline DistilBERT) | hybrid
_EXTRACTOR_MODE_RAW = os.getenv("EXTRACTOR_MODE", "hybrid").strip().lower()
EXTRACTOR_MODE = (
    _EXTRACTOR_MODE_RAW
    if _EXTRACTOR_MODE_RAW in {"regex", "ner", "hybrid"}
    else "hybrid"
)
NER_MODEL_DIR = Path(
    os.getenv("NER_MODEL_DIR", BASE_DIR / "app" / "ml" / "ner_model")
).resolve()

SYSTEM_DISCLAIMER = (
    "This system is a compliance-screening and decision-support tool. "
    "Automated findings are potential issues only and are not a final legal "
    "determination. A human reviewer must confirm before any enforcement action."
)


def local_base() -> str:
    """Address this process can use to fetch its own DemoMart pages."""
    host = "127.0.0.1" if HOST in {"0.0.0.0", "::"} else HOST
    return f"http://{host}:{PORT}"


def public_base() -> str:
    """Origin the visitor used. Falls back to this machine when there is no request."""
    try:
        from flask import has_request_context, request

        if has_request_context():
            return request.url_root.rstrip("/")
    except Exception:
        pass
    return local_base()


def dashboard_href() -> str:
    """Live Vite app on this machine. Any other host gets the same-origin dashboard."""
    try:
        from flask import has_request_context, request

        if has_request_context():
            host = (request.host or "").split(":")[0].strip().lower()
            if host and host not in {"127.0.0.1", "localhost"}:
                return "/"
    except Exception:
        pass
    return "http://127.0.0.1:5173/"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
