"""Product page scraper for real e-commerce URLs.

Strategy (free, educational mini-project):
  1. HTTP fetch with a real browser User-Agent + headers
  2. Parse with BeautifulSoup (Amazon / Flipkart / generic selectors + JSON-LD)
  3. If content looks blocked / empty / JS shell → optional Playwright render
  4. Never invent product fields — return whatever text is actually present

Major marketplaces may still block data-centre IPs or serve CAPTCHAs.
In that case the API returns a clear error and the UI offers paste-HTML fallback.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# Real browser UA — bot-style UAs are blocked immediately by Amazon/Flipkart
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)
TIMEOUT = 20


def normalize_product_url(url: str) -> str:
    """Accept messy pastes: missing scheme, www-only, or /demo/... paths."""
    u = (url or "").strip().strip('"').strip("'")
    if not u:
        return ""
    if u.startswith("/demo/"):
        return "http://127.0.0.1:5000" + u
    if re.match(r"^(127\.0\.0\.1|localhost)(:\d+)?(/|$)", u, re.I):
        return "http://" + u
    if not re.match(r"^https?://", u, re.I):
        return "https://" + u.lstrip("/")
    return u

BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def _platform_from_url(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if "amazon." in host:
        return "Amazon"
    if "flipkart." in host:
        return "Flipkart"
    if "myntra." in host:
        return "Myntra"
    if "meesho." in host:
        return "Meesho"
    if "bigbasket." in host:
        return "BigBasket"
    if "jiomart." in host:
        return "JioMart"
    if "127.0.0.1" in host or "localhost" in host:
        return "DemoMart"
    return host or "unknown"


def _looks_blocked(html: str, title: str = "") -> bool:
    blob = f"{title}\n{html[:4000]}".lower()
    signals = (
        "captcha",
        "robot check",
        "enter the characters you see",
        "api-services-support@amazon",
        "to discuss automated access",
        "continue shopping",
        "validatecaptcha",
        "sorry, we just need to make sure you're not a robot",
        "access denied",
        "request blocked",
        "cf-browser-verification",
        "attention required",
        "verify you are a human",
        "enable javascript",
        "please enable cookies",
    )
    if any(s in blob for s in signals):
        return True
    # Very thin Amazon shell
    if "amazon" in blob and len(html) < 5000 and "producttitle" not in blob:
        if "nav-logo" in blob or "gateway" in blob:
            return True
    return False


def _extract_json_ld(soup: BeautifulSoup) -> list[str]:
    chunks: list[str] = []
    for tag in soup.find_all("script", type="application/ld+json"):
        raw = tag.string or tag.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            chunks.append(raw[:3000])
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            # Flatten Product / Offer graph into searchable text
            parts = []
            for key in (
                "name",
                "description",
                "brand",
                "sku",
                "gtin13",
                "gtin",
                "mpn",
                "category",
            ):
                val = item.get(key)
                if isinstance(val, dict):
                    val = val.get("name") or val.get("@type")
                if val:
                    parts.append(f"{key}: {val}")
            offers = item.get("offers")
            if isinstance(offers, dict):
                if offers.get("price"):
                    parts.append(f"price: {offers.get('price')} {offers.get('priceCurrency', '')}")
                if offers.get("priceCurrency"):
                    parts.append(f"currency: {offers['priceCurrency']}")
            elif isinstance(offers, list):
                for off in offers[:3]:
                    if isinstance(off, dict) and off.get("price"):
                        parts.append(f"price: {off.get('price')}")
            # Additional properties often carry country of origin etc.
            for prop in item.get("additionalProperty") or []:
                if isinstance(prop, dict):
                    n, v = prop.get("name"), prop.get("value")
                    if n and v:
                        parts.append(f"{n}: {v}")
            if parts:
                chunks.append(" | ".join(str(p) for p in parts))
    return chunks


def _extract_meta(soup: BeautifulSoup) -> list[str]:
    chunks = []
    for prop in ("og:title", "og:description", "twitter:title", "twitter:description"):
        tag = soup.find("meta", property=prop) or soup.find("meta", attrs={"name": prop})
        if tag and tag.get("content"):
            chunks.append(tag["content"].strip())
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        chunks.append(md["content"].strip())
    return chunks


def _amazon_chunks(soup: BeautifulSoup) -> list[str]:
    selectors = (
        "#productTitle",
        "#title",
        "#feature-bullets",
        "#featurebullets_feature_div",
        "#detailBullets_feature_div",
        "#detailBulletsWrapper_feature_div",
        "#productDetails_techSpec_section_1",
        "#productDetails_detailBullets_sections1",
        "#prodDetails",
        "#important-information",
        "#productDescription",
        "#aplus",
        "#twister",
        "table.prodDetTable",
        "#centerCol",
        "#bylineInfo",
        ".po-break-word",
        "#productOverview_feature_div",
    )
    chunks: list[str] = []
    for sel in selectors:
        for el in soup.select(sel):
            t = el.get_text(" ", strip=True)
            if t and len(t) > 2:
                chunks.append(t)
    # Detail bullets as "label : value"
    for row in soup.select("#detailBullets_feature_div li, #detailBulletsWrapper_feature_div li"):
        t = row.get_text(" ", strip=True)
        if t:
            chunks.append(t.replace("\u200f", " ").replace("\u200e", " "))
    return chunks


def _flipkart_chunks(soup: BeautifulSoup) -> list[str]:
    selectors = (
        "span.B_NuCI",
        "span.VU-ZEz",
        "h1 span",
        "div._1mXcCf",
        "div._2418kt",
        "div._3k-BhJ",
        "table._14cfVK",
        "div._1AN87F",
        "div.X3BRps",
        "div._1AtVbE",
        "div.col-12-12",
    )
    chunks: list[str] = []
    for sel in selectors:
        for el in soup.select(sel):
            t = el.get_text(" ", strip=True)
            if t and len(t) > 2:
                chunks.append(t)
    # Spec rows
    for row in soup.select("table tr, div.row"):
        t = row.get_text(" ", strip=True)
        if t and any(
            k in t.lower()
            for k in (
                "mrp",
                "quantity",
                "origin",
                "manufacturer",
                "weight",
                "country",
                "pack",
            )
        ):
            chunks.append(t)
    return chunks


def _generic_chunks(soup: BeautifulSoup) -> list[str]:
    selectors = (
        "h1",
        "[itemprop='name']",
        "[itemprop='description']",
        ".product-title",
        ".product-details",
        "#productTitle",
        "table",
        "dl",
    )
    chunks: list[str] = []
    for sel in selectors:
        for el in soup.select(sel):
            t = el.get_text(" ", strip=True)
            if t and len(t) > 3:
                chunks.append(t)
    return chunks


def _extract_images(soup: BeautifulSoup, base_host: str = "") -> list[str]:
    images: list[str] = []
    # Amazon high-res candidates
    for img in soup.find_all("img"):
        candidates = [
            img.get("data-old-hires"),
            img.get("data-a-dynamic-image"),
            img.get("data-src"),
            img.get("src"),
        ]
        for src in candidates:
            if not src:
                continue
            if src.strip().startswith("{"):
                # Amazon dynamic image JSON
                try:
                    data = json.loads(src)
                    for k in data.keys():
                        if k.startswith("http") and k not in images:
                            images.append(k)
                except json.JSONDecodeError:
                    pass
                continue
            if src.startswith("//"):
                src = "https:" + src
            if src.startswith("/"):
                src = f"https://{base_host}{src}" if base_host else src
            if not src.startswith("http"):
                continue
            low = src.lower()
            if any(
                x in low
                for x in (
                    "sprite",
                    "icon",
                    "logo",
                    "pixel",
                    "1x1",
                    ".svg",
                    "grey-pixel",
                    "spinner",
                    "loading",
                    "transparent-pixel",
                )
            ):
                continue
            if src not in images:
                images.append(src)
        if len(images) >= 15:
            break
    return images[:12]


def parse_html_to_product(
    html: str,
    url: str = "",
    method: str = "http",
) -> dict[str, Any]:
    """Parse raw HTML (from requests, Playwright, or user paste) into product text."""
    platform = _platform_from_url(url) if url else "unknown"
    result: dict[str, Any] = {
        "ok": False,
        "source_url": url,
        "platform": platform,
        "title": None,
        "page_text": "",
        "image_urls": [],
        "error": None,
        "raw_meta": {"method": method, "html_length": len(html or "")},
    }
    if not html or len(html.strip()) < 50:
        result["error"] = "Empty HTML"
        return result

    soup = BeautifulSoup(html, "lxml")
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        title = og["content"].strip()
    result["title"] = title

    if _looks_blocked(html, title):
        result["error"] = (
            "Marketplace blocked automated access (CAPTCHA / bot wall)."
        )
        result["error_code"] = "marketplace_blocked"
        result["raw_meta"]["blocked"] = True
        return result

    # Remove noisy tags but keep text from main content
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        # keep ld+json already extracted
        if tag.name == "script" and tag.get("type") == "application/ld+json":
            continue
        if tag.name == "script":
            tag.decompose()
        elif tag.name in ("style", "noscript", "svg", "iframe"):
            tag.decompose()

    chunks: list[str] = []
    chunks.extend(_extract_json_ld(BeautifulSoup(html, "lxml")))
    chunks.extend(_extract_meta(soup))

    host = (urlparse(url).hostname or "").lower() if url else ""
    if "amazon." in host or platform == "Amazon":
        chunks.extend(_amazon_chunks(soup))
    elif "flipkart." in host or platform == "Flipkart":
        chunks.extend(_flipkart_chunks(soup))
    else:
        chunks.extend(_generic_chunks(soup))
        # also try amazon/flipkart selectors on demomart / others
        chunks.extend(_amazon_chunks(soup))

    # Full body fallback (capped)
    body_text = soup.get_text(" ", strip=True)
    if body_text:
        chunks.append(body_text[:15000])

    page_text = "\n".join(chunks)
    page_text = re.sub(r"[ \t]+", " ", page_text)
    page_text = re.sub(r"\n{3,}", "\n\n", page_text).strip()
    # Soft-normalize common marketplace labels for our field extractor
    page_text = re.sub(r"(?i)\bmaximum\s+retail\s+price\b", "MRP", page_text)
    page_text = re.sub(r"(?i)\bcountry\s+of\s+origin\b", "Country of Origin", page_text)
    page_text = re.sub(r"(?i)\bnet\s+quantity\b", "Net Quantity", page_text)
    page_text = re.sub(r"(?i)\bnet\s+weight\b", "Net Quantity", page_text)
    page_text = re.sub(r"(?i)\bitem\s+weight\b", "Net Quantity", page_text)

    result["page_text"] = page_text[:25000]
    result["image_urls"] = _extract_images(soup, host)
    result["ok"] = bool(result["page_text"] and len(result["page_text"]) > 40)

    # Detect useless shells (homepage / category landers)
    bad_titles = (
        "online shopping",
        "all categories",
        "shop by category",
        "buy products online",
    )
    title_l = (title or "").lower()
    if result["ok"] and any(b in title_l for b in bad_titles) and len(result["page_text"]) < 800:
        result["ok"] = False
        result["error"] = (
            "Fetched a generic marketplace shell, not a product page. "
            "Use a full product URL (…/dp/ASIN or …/p/…) or paste product details text."
        )
        return result

    if not result["ok"]:
        result["error"] = "Page fetched but no usable product text extracted"
    return result


def _fetch_http(url: str) -> tuple[Optional[str], Optional[str], int]:
    """Returns (html, error, status_code)."""
    try:
        session = requests.Session()
        resp = session.get(
            url.strip(),
            headers=BROWSER_HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        if resp.status_code >= 400:
            return None, f"HTTP {resp.status_code} fetching product page", resp.status_code
        return resp.text, None, resp.status_code
    except requests.Timeout:
        return None, "Request timed out while fetching product page", 0
    except requests.RequestException as exc:
        return None, f"Network error: {exc.__class__.__name__}", 0


def _fetch_playwright(url: str) -> tuple[Optional[str], Optional[str]]:
    """Render page with headless Chromium if Playwright is installed."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "playwright_not_installed"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=USER_AGENT,
                locale="en-IN",
                viewport={"width": 1366, "height": 900},
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            # Give product widgets a moment to hydrate
            page.wait_for_timeout(2500)
            # Try dismiss common cookie banners
            for sel in (
                "#sp-cc-accept",
                "input#sp-cc-accept",
                "button:has-text('Accept')",
                "button:has-text('Continue shopping')",
            ):
                try:
                    page.locator(sel).first.click(timeout=800)
                except Exception:
                    pass
            html = page.content()
            browser.close()
            return html, None
    except Exception as exc:  # noqa: BLE001
        return None, f"Playwright failed: {exc.__class__.__name__}: {exc}"


def scrape_product_url(url: str, use_browser: bool = True) -> dict[str, Any]:
    """Fetch + parse a real product URL.

    Tries HTTP first, then Playwright if available and needed.
    """
    result: dict[str, Any] = {
        "ok": False,
        "source_url": url,
        "platform": _platform_from_url(url) if url else "unknown",
        "title": None,
        "page_text": "",
        "image_urls": [],
        "error": None,
        "raw_meta": {},
    }

    url = normalize_product_url(url)
    result["source_url"] = url
    result["platform"] = _platform_from_url(url) if url else "unknown"

    if not url or not re.match(r"^https?://", url, re.I):
        result["error"] = "Invalid URL — paste a full product link (http:// or https://)"
        return result

    html, err, status = _fetch_http(url)
    methods_tried = ["http"]

    if html:
        parsed = parse_html_to_product(html, url=url, method="http")
        if parsed.get("ok"):
            parsed["raw_meta"]["http_status"] = status
            return parsed
        # Keep partial for potential upgrade
        result = parsed
        result["raw_meta"]["http_status"] = status
        result["raw_meta"]["http_error"] = parsed.get("error")
    else:
        result["error"] = err
        result["raw_meta"]["http_status"] = status

    # Playwright: skip localhost (DemoMart is already HTML), skip hard blocks
    # (CAPTCHA / 403 / 404) so the UI does not spin 45s and look "broken".
    host = (urlparse(url).hostname or "").lower()
    local = host in {"127.0.0.1", "localhost"}
    blocked = bool(
        result.get("error_code") == "marketplace_blocked"
        or (result.get("raw_meta") or {}).get("blocked")
    )
    hard_http = status in {401, 403, 404, 410, 429, 451}
    if use_browser and not local and not blocked and not hard_http:
        html2, err2 = _fetch_playwright(url)
        methods_tried.append("playwright")
        if err2 == "playwright_not_installed":
            result["raw_meta"]["playwright"] = "not_installed"
            result["raw_meta"]["methods_tried"] = methods_tried
            if not result.get("ok"):
                hint = (
                    " Tip: install Playwright for better real-site rendering: "
                    "pip install playwright && playwright install chromium"
                )
                if result.get("error"):
                    result["error"] = result["error"] + hint
                else:
                    result["error"] = "Could not extract product page." + hint
            return result
        if html2:
            parsed2 = parse_html_to_product(html2, url=url, method="playwright")
            parsed2["raw_meta"]["methods_tried"] = methods_tried
            if parsed2.get("ok"):
                return parsed2
            # Prefer richer text even if flagged
            if len(parsed2.get("page_text") or "") > len(result.get("page_text") or ""):
                result = parsed2
                result["raw_meta"]["methods_tried"] = methods_tried
        else:
            result["raw_meta"]["playwright_error"] = err2

    result["raw_meta"]["methods_tried"] = methods_tried
    if not result.get("ok") and not result.get("error"):
        result["error"] = "Could not extract product details from URL"
    return result


def scrape_from_html(html: str, url: str = "") -> dict[str, Any]:
    """Parse user-pasted page HTML (from browser View Source / Save)."""
    return parse_html_to_product(html, url=url or "pasted://html", method="user_html")


def guess_name_from_text(page_text: str, title: Optional[str]) -> str:
    if title:
        name = re.split(
            r"\s*[|\-–]\s*Amazon|\s*[|\-–]\s*Flipkart|\s*[|\-–]\s*DemoMart",
            title,
        )[0].strip()
        if name and "online shopping" not in name.lower():
            return name[:200]
    if page_text:
        return page_text[:80].strip() + ("…" if len(page_text) > 80 else "")
    return "Unknown product"


def playwright_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401

        return True
    except ImportError:
        return False
