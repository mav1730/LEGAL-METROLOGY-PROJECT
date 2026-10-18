"""Flask application entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python app/main.py` and `python -m app.main`
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS

from app.config import (
    EXTRACTOR_MODE,
    HOST,
    PORT,
    SECRET_KEY,
    SYSTEM_DISCLAIMER,
    ensure_dirs,
    public_base,
)
from app.demo_store.catalog import PRODUCTS, get_product, list_products
from app.demo_store.render import render_home, render_product, render_product_list
from app.routes.api import api_bp
from app.services.storage import init_db

DEMO_STATIC = Path(__file__).resolve().parent / "demo_store" / "static"


def _base_url() -> str:
    """Origin for copied DemoMart links. Loopback when this process is bound to all interfaces."""
    return public_base()


def create_app() -> Flask:
    ensure_dirs()
    init_db()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB uploads

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(api_bp, url_prefix="/api")

    # Warm NER once at process start so the first viva scan is not a 10s load.
    try:
        from app.field_extractor.ner_extractor import extract_fields_ner, ner_available

        if ner_available():
            extract_fields_ner("warmup")
    except Exception:  # noqa: BLE001
        pass

    frontend_dist = BACKEND_ROOT.parent / "frontend" / "dist"

    def _service_card():
        base = _base_url()
        return {
            "service": "AI Legal Metrology & E-Commerce Compliance Checker",
            "version": "1.0.0",
            "api_base": "/api",
            "health": "/api/health",
            "demo_store": f"{base}/demo/",
            "dashboard": f"{base}/",
            "demo_product_urls": [
                f"{base}/demo/dp/{slug}" for slug in PRODUCTS.keys()
            ],
            "disclaimer": SYSTEM_DISCLAIMER,
        }

    @app.get("/api/about")
    def about():
        return jsonify(_service_card())

    @app.get("/")
    def root():
        index = frontend_dist / "index.html"
        if index.is_file():
            return send_from_directory(frontend_dist, "index.html")
        return jsonify(_service_card())

    @app.get("/assets/<path:filename>")
    def spa_assets(filename: str):
        assets = frontend_dist / "assets"
        if not (assets / filename).is_file():
            return jsonify({"error": "asset not found"}), 404
        return send_from_directory(assets, filename)

    # ------------------------------------------------------------------
    # DemoMart — Amazon-style educational storefront
    # ------------------------------------------------------------------
    @app.get("/demo/")
    @app.get("/demo")
    def demo_home():
        return Response(render_home(_base_url()), mimetype="text/html")

    @app.get("/demo/products")
    def demo_products():
        return Response(render_product_list(_base_url()), mimetype="text/html")

    @app.get("/demo/dp/<slug>")
    def demo_product_page(slug: str):
        product = get_product(slug)
        if not product:
            return (
                jsonify(
                    {
                        "error": "Product not found",
                        "available": list(PRODUCTS.keys()),
                    }
                ),
                404,
            )
        return Response(render_product(product, _base_url()), mimetype="text/html")

    # Amazon-like short URL alias
    @app.get("/demo/gp/product/<asin>")
    def demo_by_asin(asin: str):
        for p in list_products():
            if p["asin"].lower() == asin.lower():
                return Response(render_product(p, _base_url()), mimetype="text/html")
        return jsonify({"error": "ASIN not found"}), 404

    @app.get("/demo/static/<path:filename>")
    def demo_static(filename: str):
        target = DEMO_STATIC / filename
        if not target.is_file() and filename.startswith("images/"):
            svg = (
                '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">'
                '<rect width="400" height="400" fill="#181824"/>'
                '<rect x="20" y="20" width="360" height="360" rx="16" fill="#222232" stroke="rgba(255,107,0,0.4)" stroke-width="2"/>'
                '<circle cx="200" cy="160" r="50" fill="rgba(255,107,0,0.15)" stroke="#ff6b00" stroke-width="2"/>'
                '<text x="200" y="172" fill="#ff9f1c" font-size="34" font-family="sans-serif" font-weight="bold" text-anchor="middle">📦</text>'
                '<text x="200" y="250" fill="#ffffff" font-size="20" font-family="sans-serif" font-weight="bold" text-anchor="middle">DemoMart Product</text>'
                '<text x="200" y="278" fill="#9ba1b0" font-size="14" font-family="sans-serif" text-anchor="middle">Legal Metrology Packaging Sample</text>'
                '</svg>'
            )
            return Response(svg, mimetype="image/svg+xml")
        return send_from_directory(DEMO_STATIC, filename)

    # Back-compat old simple demo URLs → redirect-style render
    @app.get("/demo/products/<legacy>")
    def demo_legacy(legacy: str):
        mapping = {
            "honey": "hive-organic-honey-500g",
            "oil": "pure-groundnut-oil-1l",
            "chips": "crunchyco-spicy-chips-50g",
        }
        slug = mapping.get(legacy)
        if not slug:
            return demo_products()
        product = get_product(slug)
        return Response(render_product(product, _base_url()), mimetype="text/html")

    @app.get("/app")
    @app.get("/app/<path:path>")
    def serve_frontend(path: str = "index.html"):
        if not frontend_dist.is_dir():
            return (
                jsonify(
                    {
                        "message": "Frontend not built. Run the Vite dev server or npm run build.",
                        "dev": "cd frontend && npm install && npm run dev",
                        "demo_store": "/demo/",
                    }
                ),
                404,
            )
        target = frontend_dist / path
        if path == "index.html" or not target.is_file():
            return send_from_directory(frontend_dist, "index.html")
        return send_from_directory(frontend_dist, path)

    return app


app = create_app()


if __name__ == "__main__":
    import os

    debug = os.getenv("FLASK_DEBUG", "0") not in ("0", "false", "False", "")
    print(f"Starting Legal Metrology Compliance Checker on http://{HOST}:{PORT}")
    print(f"DemoMart storefront: http://{HOST}:{PORT}/demo/")
    print(f"EXTRACTOR_MODE={EXTRACTOR_MODE}  debug={debug}")
    print(SYSTEM_DISCLAIMER)
    app.run(host=HOST, port=PORT, debug=debug, use_reloader=debug)
