#!/usr/bin/env python3
"""
regenerate_html.py - Regenerate sites/v3/index.html bookshelf from content/books.json

This is the single source of truth - all HTML is generated from JSON.
"""

import json
import re

YEAR_WIDTH = 5
TITLE_WIDTH = 73

def load_books(json_file):
    """Load books from canonical JSON."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data['books']

def format_ascii_table(books):
    """Generate perfect ASCII table from books."""
    lines = []

    # Header
    header = f"+{'-' * (YEAR_WIDTH + 2)}+{'-' * (TITLE_WIDTH + 2)}+"
    lines.append(header)

    # Books
    for book in books:
        title = book['title']

        # Truncate or pad title
        if len(title) > TITLE_WIDTH:
            title = title[:TITLE_WIDTH]
        title_padded = title.ljust(TITLE_WIDTH)

        # Format year
        if book['yearLabel']:
            year_str = book['yearLabel']  # e.g., "<2015"
        elif book['year']:
            year_str = f" {book['year']}"  # Leading space for regular years
        else:
            year_str = "  ???"

        year_padded = year_str.ljust(YEAR_WIDTH)

        line = f"| {year_padded} | {title_padded} |"
        lines.append(line)

    # Footer
    lines.append(header)

    return '\n'.join(lines)

def update_html(html_file, ascii_table):
    """Replace bookshelf section in HTML with new table."""
    with open(html_file, 'r') as f:
        html = f.read()

    # Find the bookshelf section
    start_marker = '            <pre class="book-list">'
    end_marker = '</pre>'

    start_idx = html.find(start_marker)
    if start_idx == -1:
        raise ValueError("Could not find bookshelf start marker")

    end_idx = html.find(end_marker, start_idx)
    if end_idx == -1:
        raise ValueError("Could not find bookshelf end marker")

    # Include the </pre> tag
    end_idx += len(end_marker)

    # Replace the section
    new_html = html[:start_idx] + start_marker + ascii_table + end_marker + html[end_idx:]

    with open(html_file, 'w') as f:
        f.write(new_html)

def main():
    books_json = 'content/books.json'
    html_file = 'sites/v3/index.html'

    print(f"Loading books from {books_json}...")
    books = load_books(books_json)
    print(f"Loaded {len(books)} books")

    print("\nGenerating ASCII table...")
    ascii_table = format_ascii_table(books)

    # Verify all lines are same width
    lines = ascii_table.split('\n')
    widths = [len(line) for line in lines]
    if len(set(widths)) == 1:
        print(f"✓ All {len(lines)} lines are exactly {widths[0]} characters")
    else:
        print(f"✗ ERROR: Lines have different widths: {set(widths)}")
        return

    print(f"\nUpdating {html_file}...")
    update_html(html_file, ascii_table)

    print(f"✓ Successfully regenerated bookshelf in {html_file}")
    print(f"  - {len(books)} books")
    print(f"  - {len(lines)} lines")
    print(f"  - {widths[0]} chars per line")

if __name__ == '__main__':
    main()
