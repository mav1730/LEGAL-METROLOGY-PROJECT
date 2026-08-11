"""HTML renderers for DemoMart (Amazon-inspired layout)."""

from __future__ import annotations

from html import escape
from typing import Any
from urllib.parse import quote

from app.demo_store.catalog import list_products


def _stars(rating: float) -> str:
    full = int(rating)
    half = 1 if rating - full >= 0.4 else 0
    empty = 5 - full - half
    return "★" * full + (" trace" if half else "") + "☆" * empty


def layout(title: str, body: str, active: str = "home") -> str:
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{escape(title)}</title>
  <meta name="description" content="DemoMart educational Amazon-style store for Legal Metrology compliance checker demos."/>
  <link rel="stylesheet" href="/demo/static/css/store.css"/>
</head>
<body>
  <div class="demo-banner">
    <strong>DEMO STORE ONLY</strong> — Not affiliated with Amazon.
    Educational clone for Legal Metrology mini-project testing.
    Paste product URLs into the compliance dashboard.
  </div>
  <header class="nav">
    <a class="logo" href="/demo/">demo<span>mart</span>.in</a>
    <div class="loc"><span>Delivering to</span><b>Mumbai 400001</b></div>
    <form class="search" action="/demo/" method="get" onsubmit="return false;">
      <select aria-label="Search category"><option>All</option><option>Grocery</option></select>
      <input type="search" name="q" placeholder="Search DemoMart" aria-label="Search"/>
      <button type="button" aria-label="Search">🔍</button>
    </form>
    <div class="nav-right">
      <a href="/demo/"><span>Hello, Examiner</span><span class="line2">Account &amp; Lists</span></a>
      <a href="/demo/"><span>Returns</span><span class="line2">&amp; Orders</span></a>
      <a href="/demo/"><span class="line2">🛒 Cart</span></a>
    </div>
  </header>
  <nav class="subnav">
    <a href="/demo/">All</a>
    <a href="/demo/">Fresh</a>
    <a href="/demo/">Grocery</a>
    <a href="/demo/#products">Today's Deals</a>
    <a href="/demo/products">All Products</a>
    <a href="http://127.0.0.1:5173/" target="_blank" rel="noopener">Open Compliance Checker →</a>
  </nav>
  {body}
  <footer class="footer">
    <div class="logo-f">demo<span>mart</span>.in</div>
    <p>Educational Amazon-style demo · Not a real marketplace · No payments · Local mini-project only</p>
    <p>
      <a href="/demo/">Home</a>
      <a href="/demo/products">Products</a>
      <a href="/api/health">API Health</a>
    </p>
  </footer>
  <script src="/demo/static/js/store.js"></script>
</body>
</html>
"""


def render_home(base_url: str = "http://127.0.0.1:5000") -> str:
    cards = []
    for p in list_products():
        img = p["images"][0]
        cards.append(
            f"""
            <article class="card">
              <a href="/demo/dp/{escape(p['slug'])}">
                <img src="/demo/static/images/{escape(img)}" alt="{escape(p['title'][:80])}"/>
              </a>
              <a class="title" href="/demo/dp/{escape(p['slug'])}">{escape(p['title'])}</a>
              <div class="stars">{_stars(p['rating'])}<span>{p['reviews']:,}</span></div>
              <div class="price-row">
                <span class="symbol">₹</span><span class="amount">{p['price']}</span>
                <span class="mrp-strike">M.R.P: ₹{p['mrp']}</span>
              </div>
              <div class="prime">Demo Delivery</div>
              <div style="font-size:11px;color:#565959;margin-top:6px;">{escape(p['scenario_label'])}</div>
            </article>
            """
        )

    body = f"""
    <main class="page">
      <section class="hero">
        <h1>DemoMart — Amazon-style demo storefront</h1>
        <p>
          Fake product pages with images, prices, and Legal Metrology-style declarations
          (MRP, net quantity, manufacturer, country of origin, dates).
          Use these product links in the Compliance Checker <b>Product URL</b> tab.
        </p>
        <div class="scan-hint">
          <b>How to test:</b> Copy a product link below → open
          <a href="http://127.0.0.1:5173/" target="_blank" rel="noopener">Compliance Dashboard</a>
          → <b>Product URL</b> → paste → Scan.<br/>
          Example:
          <code>{escape(base_url)}/demo/dp/hive-organic-honey-500g</code>
        </div>
      </section>
      <h2 class="section-title" id="products">Featured grocery products</h2>
      <div class="grid">
        {''.join(cards)}
      </div>
    </main>
    """
    return layout("DemoMart.in: Online Shopping", body)


def render_product_list(base_url: str = "http://127.0.0.1:5000") -> str:
    rows = []
    for p in list_products():
        url = f"{base_url}/demo/dp/{p['slug']}"
        rows.append(
            f"""
            <tr>
              <td><img src="/demo/static/images/{escape(p['images'][0])}" alt="" style="width:64px;height:64px;object-fit:contain"/></td>
              <td>
                <a href="/demo/dp/{escape(p['slug'])}"><b>{escape(p['title'][:90])}</b></a><br/>
                <span style="color:#565959;font-size:12px">{escape(p['scenario_label'])}</span>
              </td>
              <td>₹{p['price']}</td>
              <td><code style="font-size:11px">{escape(url)}</code></td>
            </tr>
            """
        )
    body = f"""
    <main class="page">
      <div class="breadcrumb"><a href="/demo/">Home</a> › All Products</div>
      <div class="details-panel">
        <h2>All demo products — copy URL for scanner</h2>
        <table class="prod-details">
          <tr><th>Image</th><th>Product</th><th>Price</th><th>Product URL</th></tr>
          {''.join(rows)}
        </table>
      </div>
    </main>
    """
    return layout("All Products — DemoMart", body, active="products")


def render_product(p: dict[str, Any], base_url: str = "http://127.0.0.1:5000") -> str:
    thumbs = []
    for i, img in enumerate(p["images"]):
        cls = "active" if i == 0 else ""
        thumbs.append(
            f'<img class="{cls}" src="/demo/static/images/{escape(img)}" data-full="/demo/static/images/{escape(img)}" alt="Product image {i+1}"/>'
        )

    fields = p.get("fields") or {}

    def _strip_label(val: str | None, prefixes: tuple[str, ...]) -> str:
        if not val:
            return "—"
        s = str(val)
        for pref in prefixes:
            if s.lower().startswith(pref.lower()):
                s = s[len(pref) :].lstrip(" :")
        return s

    # Amazon-style technical details.
    # Cell values are plain (no second "Manufactured by" prefix) to avoid dual matches.
    mrp_cell = _strip_label(fields.get("mrp"), ("MRP", "Maximum Retail Price"))
    qty_cell = _strip_label(fields.get("net_quantity"), ("Net Quantity", "Net Qty"))
    mfg_cell = _strip_label(fields.get("manufacturer"), ("Manufactured by", "Manufacturer"))
    origin_cell = _strip_label(fields.get("country_of_origin"), ("Country of Origin", "Made in"))
    mfd_cell = _strip_label(fields.get("manufacturing_date"), ("Mfg Date", "Date of Manufacture"))
    exp_cell = _strip_label(fields.get("expiry_date"), ("Best Before", "Exp Date", "Expiry Date"))
    pname_cell = _strip_label(fields.get("product_name"), ("Product Name",))

    mapping = [
        ("ASIN", p["asin"]),
        ("Brand", p["brand"]),
        ("Product Dimensions", "Standard retail pack"),
        ("Best Sellers Rank", "#Demo in Grocery & Gourmet Foods"),
    ]
    detail_rows = []
    for label, value in mapping:
        detail_rows.append(
            f"<tr><th>{escape(str(label))}</th><td>{escape(str(value))}</td></tr>"
        )

    # Single labeled block for Legal Metrology (one declaration per field)
    lm_lines = []
    if fields.get("product_name"):
        lm_lines.append(fields["product_name"] if str(fields["product_name"]).lower().startswith("product") else f"Product Name: {pname_cell}")
    if fields.get("mrp"):
        lm_lines.append(fields["mrp"] if str(fields["mrp"]).upper().startswith("MRP") else f"MRP Rs. {mrp_cell}")
    if fields.get("net_quantity"):
        lm_lines.append(fields["net_quantity"] if "net" in str(fields["net_quantity"]).lower() else f"Net Quantity: {qty_cell}")
    if fields.get("manufacturer"):
        lm_lines.append(
            fields["manufacturer"]
            if "manufactured" in str(fields["manufacturer"]).lower()
            else f"Manufactured by: {mfg_cell}"
        )
    if fields.get("country_of_origin"):
        lm_lines.append(fields["country_of_origin"])
    if fields.get("manufacturing_date"):
        lm_lines.append(fields["manufacturing_date"])
    if fields.get("expiry_date"):
        lm_lines.append(fields["expiry_date"])
    if fields.get("customer_care"):
        lm_lines.append(fields["customer_care"])
    if fields.get("fssai"):
        lm_lines.append(fields["fssai"])

    lm_html = "".join(f"<p>{escape(str(line))}</p>" for line in lm_lines) if lm_lines else "<p>Limited information on this sparse listing.</p>"

    bullets = "".join(f"<li>{escape(b)}</li>" for b in p["bullets"])
    product_url = f"{base_url}/demo/dp/{p['slug']}"

    # Optional OCR conflict note for dual-source demos
    ocr_extra = ""
    if p.get("ocr_conflict_note"):
        ocr_extra = (
            f'<p class="packaging-ocr-text">Packaging print sample: '
            f'{escape(p["ocr_conflict_note"])} Net Quantity 100 g Made in India</p>'
        )

    body = f"""
    <main class="page">
      <div class="breadcrumb">
        <a href="/demo/">Home</a> › {escape(p['category'])}
      </div>
      <div class="scan-hint">
        <b>Product URL for Compliance Checker:</b>
        <code id="product-url">{escape(product_url)}</code>
        <button type="button" class="btn btn-cart" style="width:auto;display:inline-block;margin:6px 0 0;padding:6px 14px"
          onclick="navigator.clipboard.writeText(document.getElementById('product-url').textContent)">
          Copy URL
        </button>
      </div>

      <div class="pdp">
        <div class="thumbs" id="thumbs">
          {''.join(thumbs)}
        </div>
        <div class="main-img-wrap">
          <img id="main-image" src="/demo/static/images/{escape(p['images'][0])}"
               alt="{escape(p['title'][:100])}"/>
        </div>
        <div>
          <div class="pdp-info">
            <h1 id="productTitle">{escape(p['title'])}</h1>
            <div class="brand-line">Visit the <a href="/demo/">{escape(p['brand'])}</a> Store</div>
            <div class="rating-line">
              <span class="stars">{_stars(p['rating'])}</span>
              <a href="#reviews">{p['reviews']:,} ratings</a>
              &nbsp;|&nbsp; {escape(p.get('bought', ''))}
            </div>
            <div class="price-block">
              <div class="deal">Limited demo deal</div>
              <div class="big"><span class="rupee">₹</span>{p['price']}</div>
              <div class="tax-note">M.R.P.: <span style="text-decoration:line-through">₹{p['mrp']}</span>
              &nbsp;·&nbsp; {escape(p['discount_note'])}</div>
            </div>
            <div class="about">
              <b>About this item</b>
              <ul>{bullets}</ul>
            </div>
          </div>
          <div class="buybox" style="margin-top:12px">
            <div class="price">₹{p['price']}.00</div>
            <div class="stock">{"In stock" if p["in_stock"] else "Out of stock"}</div>
            <div class="ship">FREE delivery <b>Tomorrow</b> on demo orders<br/>Delivering to Mumbai 400001</div>
            <button type="button" class="btn btn-cart">Add to Cart</button>
            <button type="button" class="btn btn-buy">Buy Now</button>
            <div class="secure">🔒 Secure transaction (demo only — no payment)</div>
            <div style="font-size:12px;margin-top:10px;color:#565959">
              Sold by <b>{escape(p['brand'])} Demo Seller</b> and fulfilled by DemoMart
            </div>
          </div>
        </div>
      </div>

      <section class="details-panel" id="productDetails_techSpec_section_1">
        <h2>Product details</h2>
        <h3>Technical Details</h3>
        <table class="prod-details">
          {''.join(detail_rows)}
          <tr><th>Customer Reviews</th><td>{_stars(p['rating'])} {p['rating']} out of 5 stars</td></tr>
          <tr><th>Date First Available</th><td>1 January 2024</td></tr>
        </table>

        <h3>Product description</h3>
        <div id="productDescription" class="product-details">
          <p>{escape(p['title'])}. Brand: {escape(p['brand'])}.</p>
          <p>Premium grocery item available on DemoMart educational storefront.</p>
        </div>

        <h3>Important information</h3>
        <div id="important-information" class="product-details">
          <p><b>Legal Metrology declarations (as on pack / listing):</b></p>
          <div id="feature-bullets">
            {lm_html}
          </div>
          {ocr_extra}
          <p style="font-size:12px;color:#565959;margin-top:10px">
            Scenario: <b>{escape(p['scenario_label'])}</b>
          </p>
        </div>
      </section>
    </main>
    """
    return layout(f"{p['title'][:60]} : DemoMart.in", body)
