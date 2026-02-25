#!/usr/bin/env python3
"""
Rescrape IST website (ist.edu.pk) and update data/99_MASTER_JSON.json.
Run from project root: uv run python scrape_ist.py
Uses existing JSON to get URL list; fetches each page and updates title, text, text_blocks.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import urllib3

import requests
from bs4 import BeautifulSoup

# IST site can trigger SSL verify errors on some systems; skip verify for scraping only
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = Path(__file__).resolve().parent / "data"
MASTER_JSON = DATA_DIR / "99_MASTER_JSON.json"
REQUEST_TIMEOUT = 25
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


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
    # Remove script, style
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    # Prefer main content
    main = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|main|body", re.I))
    root = main if main else soup.body
    if not root:
        root = soup
    # Collect text from p, div, li, h1-h6
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
    # text_blocks: use blocks if we have them, else one block
    text_blocks = [b for b in blocks if len(b) > 10] if blocks else ([full] if full else [])
    if not text_blocks and full:
        text_blocks = [full]
    return title, full, text_blocks


def main():
    if not MASTER_JSON.exists():
        print("Missing", MASTER_JSON, "- create or restore 99_MASTER_JSON.json first.")
        sys.exit(1)
    with open(MASTER_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    pages = data.get("pages", {})
    urls = list(pages.keys())
    print(f"Rescraping {len(urls)} URLs...")
    ok = 0
    fail = 0
    for i, url in enumerate(urls):
        title, text, text_blocks = get_page_text(url)
        if text or title:
            pages[url]["title"] = title or pages[url].get("title", "")
            pages[url]["text"] = text
            pages[url]["text_blocks"] = text_blocks if text_blocks else [text] if text else []
            pages[url]["scraped_at"] = datetime.now(timezone.utc).isoformat()
            ok += 1
        else:
            fail += 1
        if (i + 1) % 10 == 0:
            print(f"  {i + 1}/{len(urls)}")
    total_words = sum(len(p.get("text", "").split()) for p in pages.values())
    data["metadata"] = {
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "total_pages": len(pages),
        "total_words": total_words,
    }
    with open(MASTER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Done. OK: {ok}, failed: {fail}, total words: {total_words}")


if __name__ == "__main__":
    main()
