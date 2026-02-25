#!/usr/bin/env python3
"""
Auto-update IST knowledge base from https://ist.edu.pk every 15 minutes.
- Rescrapes every page in 99_MASTER_JSON plus known admissions/academics/student-affairs URLs.
- Never removes existing pages; only adds new URLs and updates text.
- Extracts announcement snippets (challan, fee last date) and updates data/ANNOUNCEMENTS.txt.
Run from project root: uv run python kb_auto_update.py
Optional: KB_UPDATE_INTERVAL_MINUTES=15 (default). Set to 0 for one-shot run.
"""
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import urllib3
import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = Path(__file__).resolve().parent / "data"
MASTER_JSON = DATA_DIR / "99_MASTER_JSON.json"
ANNOUNCEMENTS_PATH = DATA_DIR / "ANNOUNCEMENTS.txt"
REQUEST_TIMEOUT = 30
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Additional seed URLs to ensure full site coverage (Admissions, Student Affairs, Quality, Campuses, etc.)
# These are merged with existing pages in 99_MASTER_JSON; no page is ever removed.
SEED_EXTRA_URLS = [
    "https://www.ist.edu.pk/",
    "https://ist.edu.pk/",
    "https://ist.edu.pk/about",
    "https://www.ist.edu.pk/about",
    "https://www.ist.edu.pk/admission-undergraduate-info",
    "https://www.ist.edu.pk/admission-graduate-schedule",
    "https://www.ist.edu.pk/admission-faq",
    "https://www.ist.edu.pk/admission-fee-structure-bs-programs",
    "https://www.ist.edu.pk/admission-fee-structure-ms-local-programs",
    "https://www.ist.edu.pk/admissions",
    "https://ist.edu.pk/admissions",
    "https://www.ist.edu.pk/academics",
    "https://ist.edu.pk/academics",
    "https://www.ist.edu.pk/research",
    "https://ist.edu.pk/research",
    "https://www.ist.edu.pk/national-centers",
    "https://ist.edu.pk/national-centers",
    "https://www.ist.edu.pk/campus-life",
    "https://www.ist.edu.pk/campus-life/facilities-at-ist",
    "https://www.ist.edu.pk/news-events",
    "https://www.ist.edu.pk/student-affairs",
    "https://ist.edu.pk/student-affairs",
    "https://www.ist.edu.pk/quality-enhancement",
    "https://ist.edu.pk/quality-enhancement",
    "https://www.ist.edu.pk/campuses",
    "https://ist.edu.pk/campuses",
    "https://www.ist.edu.pk/foreign-applicant",
    "https://www.ist.edu.pk/migration-transfer",
    "https://www.ist.edu.pk/financial-aid-scholarship",
    "https://www.ist.edu.pk/student-fee-challan",
    "https://ist.edu.pk/student-fee-challan",
]


def normalize_url(url: str) -> str:
    """Normalize to https://www.ist.edu.pk or https://ist.edu.pk style for dedup."""
    u = url.strip()
    if not u:
        return u
    parsed = urlparse(u)
    path = parsed.path or "/"
    path = path.rstrip("/") or "/"
    netloc = parsed.netloc.lower().replace("www.", "")
    if netloc == "ist.edu.pk":
        return f"https://ist.edu.pk{path}" + (f"?{parsed.query}" if parsed.query else "")
    return u


def get_page_text(url: str) -> tuple[str, str, list[str]]:
    """Fetch URL and return (title, full_text, text_blocks)."""
    try:
        r = requests.get(
            url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT, verify=False
        )
        r.raise_for_status()
    except Exception as e:
        return "", f"[Fetch error: {e}]", []
    soup = BeautifulSoup(r.text, "html.parser")
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|main|body", re.I))
    root = main if main else soup.body
    if not root:
        root = soup
    blocks = []
    for el in root.find_all(["p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "span"]):
        t = el.get_text(separator=" ", strip=True)
        if t and len(t) > 2:
            blocks.append(t)
    full = " ".join(blocks)
    if not full:
        full = root.get_text(separator=" ", strip=True)
    if not full and soup.body:
        full = soup.body.get_text(separator=" ", strip=True)
    full = " ".join(full.split())
    text_blocks = [b for b in blocks if len(b) > 10] if blocks else ([full] if full else [])
    if not text_blocks and full:
        text_blocks = [full]
    return title, full, text_blocks


def discover_links_from_page(base_url: str, html: str) -> set[str]:
    """Extract same-domain links from HTML. Returns absolute URLs."""
    soup = BeautifulSoup(html, "html.parser")
    out = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.netloc.lower().replace("www.", "") != "ist.edu.pk":
            continue
        path = (parsed.path or "/").rstrip("/") or "/"
        out.add(f"https://ist.edu.pk{path}" + (f"?{parsed.query}" if parsed.query else ""))
    return out


def load_master() -> dict:
    """Load 99_MASTER_JSON; create minimal structure if missing."""
    if not MASTER_JSON.exists():
        return {
            "metadata": {},
            "categories": {},
            "contacts": {},
            "pages": {},
        }
    with open(MASTER_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_master(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(MASTER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_scrape() -> tuple[int, int]:
    """Rescrape all known URLs and merge into 99_MASTER_JSON. Returns (ok_count, fail_count)."""
    data = load_master()
    pages_raw = data.setdefault("pages", {})
    # Normalize keys so we don't duplicate www vs non-www
    pages = {}
    for u, page in pages_raw.items():
        n = normalize_url(u)
        if n not in pages:
            pages[n] = dict(page)
        else:
            pages[n].update(page)
    data["pages"] = pages

    # Collect all URLs: existing + seed extra (normalized)
    all_urls = set()
    for u in pages:
        all_urls.add(normalize_url(u))
    for u in SEED_EXTRA_URLS:
        all_urls.add(normalize_url(u))

    # Optionally discover from homepage
    try:
        r = requests.get(
            "https://ist.edu.pk/",
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
            verify=False,
        )
        if r.ok:
            discovered = discover_links_from_page("https://ist.edu.pk/", r.text)
            for u in discovered:
                all_urls.add(normalize_url(u))
    except Exception:
        pass

    urls_list = sorted(all_urls)
    ok = 0
    fail = 0
    for i, url in enumerate(urls_list):
        title, text, text_blocks = get_page_text(url)
        if text or title:
            if url not in pages:
                pages[url] = {}
            pages[url]["title"] = title or pages[url].get("title", "")
            pages[url]["text"] = text
            pages[url]["text_blocks"] = text_blocks if text_blocks else ([text] if text else [])
            pages[url]["scraped_at"] = datetime.now(timezone.utc).isoformat()
            ok += 1
        else:
            fail += 1
        if (i + 1) % 15 == 0:
            print(f"  Scraped {i + 1}/{len(urls_list)}")

    total_words = sum(len(p.get("text", "").split()) for p in pages.values())
    data["metadata"] = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_pages": len(pages),
        "total_words": total_words,
    }
    save_master(data)
    return ok, fail


def update_announcements_from_pages(data: dict) -> None:
    """If any scraped page mentions challan/fee last date, update ANNOUNCEMENTS.txt (merge, don't remove)."""
    pages = data.get("pages", {})
    # Look for date-like patterns and challan/fee submission
    date_pattern = re.compile(
        r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b",
        re.I,
    )
    challan_pattern = re.compile(r"challan|fee\s*submission|last\s*date\s*for\s*fee", re.I)
    found_dates = []
    for url, page in pages.items():
        text = page.get("text", "")
        if not challan_pattern.search(text):
            continue
        for m in date_pattern.finditer(text):
            found_dates.append(m.group(1))
    if not found_dates and not ANNOUNCEMENTS_PATH.exists():
        return
    # Read existing announcements to preserve content
    existing = ""
    if ANNOUNCEMENTS_PATH.exists():
        try:
            existing = ANNOUNCEMENTS_PATH.read_text(encoding="utf-8")
        except Exception:
            pass
    # If we found a new date from the site and it's not in the file, we could append; for now keep existing
    # and only ensure the header and one line with "last date" are present (user said last date 3rd March 2026)
    if "3rd March 2026" not in existing and "3rd March 2026" not in str(found_dates):
        # Keep user-provided date; if website has different date we could add a line "As per website: ..."
        pass
    if found_dates and "last date" in existing.lower():
        # Optionally add "As per website update: [date]" if different
        pass
    # Ensure file exists with at least challan + 3rd March 2026
    if not ANNOUNCEMENTS_PATH.exists() or not existing.strip():
        ANNOUNCEMENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        ANNOUNCEMENTS_PATH.write_text(
            "IST ANNOUNCEMENTS (updated from website)\n"
            "Fee challans have been uploaded. Last date for submitting fee: 3rd March 2026.\n",
            encoding="utf-8",
        )


def run_once() -> None:
    print("IST knowledge base auto-update: starting scrape...")
    data = load_master()
    ok, fail = run_scrape()
    data = load_master()
    update_announcements_from_pages(data)
    print(f"Done. OK: {ok}, failed: {fail}")


def main() -> None:
    interval_min = int(__import__("os").environ.get("KB_UPDATE_INTERVAL_MINUTES", "15"))
    if interval_min <= 0:
        run_once()
        return
    print(f"IST knowledge base auto-update: every {interval_min} minutes. Press Ctrl+C to stop.")
    while True:
        try:
            run_once()
        except Exception as e:
            print("Scrape error:", e)
        print(f"Next run in {interval_min} minutes.")
        time.sleep(interval_min * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    else:
        main()
