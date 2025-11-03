#!/usr/bin/env python3
"""
fix_bookshelf.py - Extract and reformat bookshelf with perfect ASCII alignment

Year column: 5 chars ( 2020 or <2015)
Title column: 73 chars
Total line width: 85 chars
"""

import re
import sys

def extract_books(html_file):
    """Extract all book entries from HTML."""
    with open(html_file, 'r') as f:
        content = f.read()

    # Find all book lines
    pattern = r'\|\s*([<\d?]+)\s*\|\s*([^|]+?)\s*\|'
    matches = re.findall(pattern, content)

    books = []
    for year, title in matches:
        year = year.strip()
        title = title.strip()

        # Skip header/footer lines
        if year.replace('-', '').replace('+', '').strip() == '':
            continue

        # Normalize year format
        if year.startswith('<'):
            year_formatted = year[:5]  # <2015
        elif year == '????':
            year_formatted = '<2015'
        else:
            year_formatted = f' {year}'  # Leading space for regular years

        books.append((year_formatted, title))

    return books

def format_bookshelf(books):
    """Format books as perfect ASCII table."""
    YEAR_WIDTH = 5
    TITLE_WIDTH = 73

    lines = []

    # Header
    header = f"+{'-' * (YEAR_WIDTH + 2)}+{'-' * (TITLE_WIDTH + 2)}+"
    lines.append(header)

    # Books
    for year, title in books:
        # Truncate or pad title
        if len(title) > TITLE_WIDTH:
            title = title[:TITLE_WIDTH]
        title_padded = title.ljust(TITLE_WIDTH)

        # Ensure year is exactly YEAR_WIDTH
        year_padded = year.ljust(YEAR_WIDTH)

        line = f"| {year_padded} | {title_padded} |"
        lines.append(line)

    # Footer
    lines.append(header)

    return lines

def main():
    html_file = 'sites/v3/index.html'

    print("Extracting books from HTML...")
    books = extract_books(html_file)
    print(f"Found {len(books)} books\n")

    print("Generating perfectly aligned table...")
    lines = format_bookshelf(books)

    print("\n" + "="*85)
    print("PREVIEW (check alignment in monospace font):")
    print("="*85)
    for line in lines:
        print(line)
    print("="*85)

    # Verify all lines are same width
    widths = [len(line) for line in lines]
    if len(set(widths)) == 1:
        print(f"\n✓ All lines are exactly {widths[0]} characters")
    else:
        print(f"\n✗ ERROR: Lines have different widths: {set(widths)}")
        for i, line in enumerate(lines):
            if len(line) != widths[0]:
                print(f"  Line {i}: {len(line)} chars - {repr(line)}")

    # Save to temp file
    output_file = '/tmp/bookshelf_preview.txt'
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    print(f"\nSaved to: {output_file}")
    print("\nTo apply: Copy the table from the preview file and replace in sites/v3/index.html")

if __name__ == '__main__':
    main()
