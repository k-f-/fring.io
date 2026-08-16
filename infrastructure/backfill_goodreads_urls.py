#!/usr/bin/env python3
"""Backfill exact GoodReads links in content/books.md.

Wraps plain-title entries as markdown links using the shelf RSS
(all pages). Keeps existing display titles verbatim; only adds link
syntax. Already-linked entries are left untouched, so this is safe to
re-run whenever shelf additions might match previously unlinked books.

Usage (from repo root):
    python3 infrastructure/backfill_goodreads_urls.py
"""

import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.request import urlopen

sys.path.insert(0, "infrastructure")
from sync_goodreads import (
    BOOKS_MD,
    RSS_URL,
    display_title,
    normalize_title,
    parse_existing_books,
    rebuild_md,
)


def fetch_all_rss_urls():
    """normalized title -> book url, across all RSS pages; collisions dropped."""
    mapping = {}
    collisions = set()
    page = 1
    while True:
        with urlopen(f"{RSS_URL}&page={page}", timeout=30) as resp:
            root = ET.fromstring(resp.read())
        items = root.findall(".//item")
        if not items:
            break
        for item in items:
            title = item.findtext("title", "").strip()
            book_id = item.findtext("book_id", "").strip()
            if not title or not book_id:
                continue
            key = normalize_title(title)
            url = f"https://www.goodreads.com/book/show/{book_id}"
            if key in mapping and mapping[key] != url:
                collisions.add(key)
            mapping[key] = url
        print(f"  page {page}: {len(items)} items")
        page += 1
    for key in collisions:
        del mapping[key]
    if collisions:
        print(f"  dropped {len(collisions)} ambiguous title(s): {sorted(collisions)}")
    return mapping


def main():
    print("Fetching RSS pages...")
    urls = fetch_all_rss_urls()
    print(f"  {len(urls)} unique titles with URLs\n")

    md_content = BOOKS_MD.read_text()
    header, sections = parse_existing_books(md_content)

    linked, missed, already = 0, 0, 0
    misses = []
    new_sections = []
    for year, label, books in sections:
        new_books = []
        for entry in books:
            if display_title(entry) != entry:  # already a link
                already += 1
                new_books.append(entry)
                continue
            url = urls.get(normalize_title(entry))
            if url:
                new_books.append(f"[{entry}]({url})")
                linked += 1
            else:
                new_books.append(entry)
                missed += 1
                misses.append(entry)
        new_sections.append((year, label, new_books))

    updated = rebuild_md(header, new_sections)
    today = datetime.now().strftime("%Y-%m-%d")
    updated = re.sub(r'"contentUpdated":\s*"[^"]*"', f'"contentUpdated": "{today}"', updated)
    BOOKS_MD.write_text(updated)

    print(f"Linked {linked}, already linked {already}, no match {missed}")
    for m in misses:
        print(f"  ~ {m}")


if __name__ == "__main__":
    main()
