"""Convenience launcher: python run.py"""

from app.main import app
from app.config import HOST, PORT, SYSTEM_DISCLAIMER

if __name__ == "__main__":
    print(f"→ http://{HOST}:{PORT}")
    print(SYSTEM_DISCLAIMER)
    app.run(host=HOST, port=PORT, debug=True)
