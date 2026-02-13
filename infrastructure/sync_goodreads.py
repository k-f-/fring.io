#!/usr/bin/env python3
"""
Sync GoodReads "read" shelf with books.md.

Fetches RSS feed, diffs against existing books, prepends new entries
under the correct year section. Creates new year sections as needed.

Usage:
    python infrastructure/sync_goodreads.py
    GOODREADS_USER_ID=2216827 python infrastructure/sync_goodreads.py
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

GOODREADS_USER_ID = os.environ.get("GOODREADS_USER_ID", "2216827")
RSS_URL = f"https://www.goodreads.com/review/list_rss/{GOODREADS_USER_ID}?shelf=read"
BOOKS_MD = Path("content/books.md")


def normalize_title(title):
    """Strip subtitles, series markers, punctuation for fuzzy title matching."""
    t = title.lower().strip()
    t = re.sub(r"\s*\([^)]*\)\s*$", "", t)
    t = t.split(":")[0].strip()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def fetch_rss_books():
    print(f"Fetching RSS: {RSS_URL}")
    with urlopen(RSS_URL, timeout=30) as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    books = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        if not title:
            continue

        read_at_raw = item.findtext("user_read_at", "").strip()
        date_added_raw = item.findtext("user_date_added", "").strip()

        year = None
        if read_at_raw:
            try:
                year = datetime.strptime(read_at_raw, "%a, %d %b %Y %H:%M:%S %z").year
            except ValueError:
                pass
        if year is None and date_added_raw:
            try:
                year = datetime.strptime(
                    date_added_raw, "%a, %d %b %Y %H:%M:%S %z"
                ).year
            except ValueError:
                pass

        books.append({"title": title, "year": year})

    print(f"  Found {len(books)} books in RSS feed")
    return books


def parse_existing_books(md_content):
    """Parse books.md into header lines + structured year sections."""
    sections = []
    header = []

    lines = md_content.split("\n")
    current_year = None
    current_label = None
    current_books = []
    in_header = True

    for line in lines:
        year_match = re.match(r"^## (.+?)(?:\s*\([^)]*\))?\s*$", line)
        if year_match:
            if not in_header:
                sections.append((current_year, current_label, current_books))
            in_header = False

            raw = year_match.group(1).strip()
            try:
                current_year = int(raw)
                current_label = None
            except ValueError:
                current_year = None
                current_label = raw
            current_books = []
        elif in_header:
            header.append(line)
        elif re.match(r"^- .+", line):
            current_books.append(line[2:].strip())

    if not in_header:
        sections.append((current_year, current_label, current_books))

    return header, sections


def rebuild_md(header, sections):
    """Rebuild books.md from header + structured sections."""
    lines = header[:]
    if lines and lines[-1].strip() != "":
        lines.append("")

    for year, label, books in sections:
        lines.append(f"## {label}" if label else f"## {year}")
        lines.append("")
        for title in books:
            lines.append(f"- {title}")
        lines.append("")

    result = "\n".join(lines)
    if not result.endswith("\n"):
        result += "\n"
    return result


def main():
    if not BOOKS_MD.exists():
        print(f"Error: {BOOKS_MD} not found. Run from repo root.")
        sys.exit(1)

    rss_books = fetch_rss_books()
    md_content = BOOKS_MD.read_text()
    header, sections = parse_existing_books(md_content)

    existing_normalized = set()
    for _, _, books in sections:
        for title in books:
            existing_normalized.add(normalize_title(title))

    new_books = [
        b
        for b in rss_books
        if b["year"] is not None
        and normalize_title(b["title"]) not in existing_normalized
    ]

    if not new_books:
        print("\nNo new books found.")
        return

    print(f"\nFound {len(new_books)} new book(s):")
    for b in new_books:
        print(f"  + {b['title']} ({b['year']})")

    by_year = {}
    for book in new_books:
        by_year.setdefault(book["year"], []).append(book["title"])

    year_to_idx = {s[0]: i for i, s in enumerate(sections) if s[0] is not None}

    added = 0
    for year, titles in sorted(by_year.items(), reverse=True):
        if year in year_to_idx:
            idx = year_to_idx[year]
            sy, label, existing_books = sections[idx]
            sections[idx] = (sy, label, titles + existing_books)
        else:
            # Find correct descending position
            insert_at = 0
            for i, (sy, _, _) in enumerate(sections):
                if sy is not None and sy > year:
                    insert_at = i + 1
                else:
                    break
            sections.insert(insert_at, (year, None, titles))
            year_to_idx = {s[0]: i for i, s in enumerate(sections) if s[0] is not None}
        added += len(titles)

    updated_md = rebuild_md(header, sections)
    BOOKS_MD.write_text(updated_md)
    print(f"\n✓ Added {added} book(s) to {BOOKS_MD}")


if __name__ == "__main__":
    main()
