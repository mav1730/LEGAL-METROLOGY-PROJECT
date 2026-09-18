"""Convenience launcher: python run.py

Debug reloader is off by default so DistilBERT is not loaded twice and the
process does not die when the parent shell is recycled. Set FLASK_DEBUG=1
only when you are editing Python and want auto-reload.
"""

import os

from app.main import app
from app.config import EXTRACTOR_MODE, HOST, PORT, SYSTEM_DISCLAIMER

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") not in ("0", "false", "False", "")
    print(f"-> http://{HOST}:{PORT}")
    print(f"EXTRACTOR_MODE={EXTRACTOR_MODE}  debug={debug}")
    print(SYSTEM_DISCLAIMER)
    app.run(host=HOST, port=PORT, debug=debug, use_reloader=debug)
