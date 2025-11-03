#!/usr/bin/env python3
"""
migrate_to_json.py - Extract books from HTML and create content/books.json

This creates a canonical, version-agnostic content store.
"""

import json
import re
import os
from datetime import datetime

def extract_books_from_html(html_file):
    """Extract all books from the v3 HTML file."""
    with open(html_file, 'r') as f:
        content = f.read()

    # Find all book lines in the ASCII table
    # Format: |  2020 | Book Title... |  or  | <2015 | Book Title... |
    pattern = r'\|\s+([<\d]+)\s+\|\s+(.+?)\s+\|'
    matches = re.findall(pattern, content)

    books = []
    for year_str, title in matches:
        year_str = year_str.strip()
        title = title.strip()

        # Skip header/footer lines
        if not year_str or year_str[0] in '+-':
            continue

        # Parse year
        if year_str.startswith('<'):
            year = None
            year_label = year_str
        else:
            try:
                year = int(year_str)
                year_label = None
            except ValueError:
                continue

        books.append({
            "title": title,
            "year": year,
            "yearLabel": year_label,
            "dateAdded": datetime.now().isoformat()
        })

    return books

def create_books_json(books, output_file):
    """Create the canonical books.json file."""
    data = {
        "meta": {
            "version": "1.0",
            "lastUpdated": datetime.now().isoformat(),
            "description": "Canonical book list for fring.io - version agnostic content"
        },
        "books": books
    }

    # Ensure content directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    return data

def main():
    html_file = 'sites/v3/index.html'
    json_file = 'content/books.json'

    print(f"Extracting books from {html_file}...")
    books = extract_books_from_html(html_file)
    print(f"Found {len(books)} books")

    print(f"\nCreating {json_file}...")
    data = create_books_json(books, json_file)

    print(f"✓ Created {json_file}")
    print(f"  - {len(books)} books")
    print(f"  - Version: {data['meta']['version']}")
    print(f"  - Last updated: {data['meta']['lastUpdated']}")

    # Show sample
    print("\nSample entries:")
    for book in books[:3]:
        year_display = book['yearLabel'] if book['yearLabel'] else f" {book['year']}"
        print(f"  [{year_display}] {book['title']}")

if __name__ == '__main__':
    main()
