#!/usr/bin/env python3
"""
Generate ASCII visualizations for fring.io v4
Uses box-drawing characters for charts, timelines, and trees
"""

import json
from datetime import datetime
from pathlib import Path

def load_books_data():
    """Load and parse books.json"""
    with open('../../content/books.json', 'r') as f:
        return json.load(f)

def load_career_data():
    """Load and parse career.json"""
    with open('../../content/career.json', 'r') as f:
        return json.load(f)

def generate_books_bar_chart():
    """Generate horizontal bar chart of books read per year"""
    data = load_books_data()

    # Count books by year and by label
    books_by_year = {}
    prior_books = 0

    for book in data['books']:
        year = book.get('year')
        year_label = book.get('yearLabel')

        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1
        elif year_label:  # Books with yearLabel (e.g., "<2015")
            prior_books += 1

    # Sort by year DESCENDING (newest first)
    years = sorted(books_by_year.items(), reverse=True)
    max_recent_books = max(books_by_year.values()) if books_by_year else 1
    max_books_for_chart = max(max_recent_books, prior_books)

    recent_total = sum(books_by_year.values())
    grand_total = recent_total + prior_books
    avg = recent_total / len(books_by_year) if books_by_year else 0

    # Create horizontal stats line with sparkline (only for recent years)
    sparkline_chars = " ▁▂▃▄▅▆▇█"
    sparkline = ""
    for year, count in sorted(books_by_year.items()):  # ascending for sparkline
        index = int((count / max_recent_books) * (len(sparkline_chars) - 1))
        sparkline += sparkline_chars[index]

    # Generate chart
    lines = []
    lines.append("READING ACTIVITY")
    lines.append(f"Total: {grand_total} books │ 2015-2020: {recent_total} │ Avg: {avg:.1f}/year │ Peak: 2017 (21) │ Trend: {sparkline}")
    lines.append("")

    for year, count in years:
        # Scale bar to max 40 characters - use continuous string
        bar_length = int((count / max_books_for_chart) * 40)
        bar = "█" * bar_length
        lines.append(f"{year} │{bar} {count}")

    # Add prior books
    if prior_books > 0:
        bar_length = int((prior_books / max_books_for_chart) * 40)
        bar = "░" * bar_length  # Use lighter shade for prior
        lines.append(f"<2015│{bar} {prior_books}")

    lines.append("     └" + "─" * 45)

    return "\n".join(lines)

def generate_career_timeline():
    """Generate vertical career timeline - progression moves upward"""
    data = load_career_data()

    lines = []
    lines.append("CAREER TRAJECTORY")
    lines.append("(Progression moves upward)")
    lines.append("")

    # Build from bottom to top (oldest to newest)
    # Reverse the experience list so oldest is first
    experiences = list(reversed(data['experience']))

    for i, exp in enumerate(experiences):
        title = exp['title']
        company = exp.get('company', 'Independent')
        start = exp['startDate'][:4]
        end = exp['endDate'][:4] if exp.get('endDate') else 'Present'

        # Vertical line and label
        if exp.get('current'):
            lines.append(f"        ▲  ◄── {title}")
            lines.append(f"        │      @ {company} ({start}-{end})")
        else:
            lines.append(f"        ├──◄── {title}")
            lines.append(f"        │      @ {company} ({start}-{end})")

        # Add vertical spacing between roles
        if i < len(experiences) - 1:
            lines.append(f"        │")

    lines.append(f"        │")
    lines.append(f"        └────── Career Start (2006)")

    return "\n".join(lines)

def generate_site_tree():
    """Generate site structure tree with clickable links"""
    lines = []
    lines.append("SITE STRUCTURE")
    lines.append("")
    lines.append('                     ┌─── Life (Location, Friends)')
    lines.append('         ┌─ <a href="#now">Now</a> ───┼─── Work (Senior Data Engineer)')
    lines.append('         │           └─── Future (Goals, Aspirations)')
    lines.append('         │')
    lines.append('fring.io─┼─ <a href="#elsewhere">Elsewhere</a> ─── Links (GitHub, LinkedIn, Goodreads)')
    lines.append('         │')
    lines.append('         │           ┌─── 2020 (9 books)')
    lines.append('         │           ├─── 2019 (6 books)')
    lines.append('         ├─ <a href="#bookshelf">Books</a> ─┼─── 2018 (12 books)')
    lines.append('         │           ├─── 2017 (21 books)')
    lines.append('         │           ├─── 2016 (15 books)')
    lines.append('         │           ├─── 2015 (3 books)')
    lines.append('         │           └─── Prior (77 books)')
    lines.append('         │')
    lines.append('         └─ <a href="#epilogue">Epilogue</a> ─── Previous versions (v1, v2, v3)')
    lines.append("")
    lines.append("     PERSONAL WEBSITE & DIGITAL GARDEN")
    lines.append("              TEXT ONLY")

    return "\n".join(lines)

if __name__ == "__main__":
    print("Generating ASCII visualizations...")
    print("\n" + "=" * 70 + "\n")

    print(generate_books_bar_chart())
    print("\n" + "=" * 70 + "\n")

    print(generate_career_timeline())
    print("\n" + "=" * 70 + "\n")

    print(generate_site_tree())
