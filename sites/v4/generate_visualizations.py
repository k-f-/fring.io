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

    # Count books by year
    books_by_year = {}
    for book in data['books']:
        year = book.get('year')
        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1

    # Sort by year
    years = sorted(books_by_year.items())
    max_books = max(books_by_year.values())

    # Generate chart
    lines = []
    lines.append("READING ACTIVITY")
    lines.append("Books Read Per Year")
    lines.append("")

    for year, count in years:
        # Scale bar to max 40 characters
        bar_length = int((count / max_books) * 40)
        bar = "█" * bar_length
        lines.append(f"{year} │{bar} {count}")

    lines.append("     └" + "─" * 45)
    lines.append(f"      Total: {sum(books_by_year.values())} books (2015-2020)")

    return "\n".join(lines)

def generate_career_timeline():
    """Generate career timeline visualization"""
    data = load_career_data()

    lines = []
    lines.append("CAREER TIMELINE")
    lines.append("")

    # Create timeline from 2006 to present
    current_year = 2025
    timeline_start = 2006
    timeline_width = 60

    # Header with year markers
    years_header = "       "
    for year in range(timeline_start, current_year + 1, 5):
        years_header += f"{year}      "
    lines.append(years_header[:timeline_width])
    lines.append("       " + "┬" + "─" * 4 + "┬" + "─" * 4 + "┬" + "─" * 4 + "┬" + "─" * 4 + "┬")

    # Plot each role
    for exp in data['experience']:
        title = exp['title']
        company = exp.get('company', '')
        start = int(exp['startDate'].split('-')[0])
        end = int(exp['endDate'].split('-')[0]) if exp.get('endDate') else current_year

        # Calculate position
        start_pos = int(((start - timeline_start) / (current_year - timeline_start)) * 40)
        end_pos = int(((end - timeline_start) / (current_year - timeline_start)) * 40)
        duration = end_pos - start_pos

        # Create bar
        bar = " " * start_pos + "├" + "─" * (duration - 1) + ("┤" if not exp.get('current') else "►")
        role_label = f"{title[:30]} @ {company[:20]}"
        lines.append(bar[:45].ljust(45) + " │ " + role_label)

    lines.append("")
    lines.append(f"Program Director @ Molina Healthcare (2023-Present)")
    lines.append(f"Senior Data Analyst/Engineer (2020-2023)")
    lines.append(f"14+ years: Network Eng, SysAdmin, DevOps (2006-2020)")

    return "\n".join(lines)

def generate_site_tree():
    """Generate site structure tree like phylogenetic example"""
    lines = []
    lines.append("SITE STRUCTURE")
    lines.append("")
    lines.append("                  ┌─── Life (Location, Friends)")
    lines.append("         ┌─ Now ─┼─── Work (Senior Data Engineer)")
    lines.append("         │        └─── Future (Goals, Aspirations)")
    lines.append("         │")
    lines.append("fring.io─┼─ Elsewhere ─── Links (GitHub, LinkedIn, Goodreads)")
    lines.append("         │")
    lines.append("         │        ┌─── 2020 (9 books)")
    lines.append("         │        ├─── 2019 (6 books)")
    lines.append("         ├─ Books─┼─── 2018 (12 books)")
    lines.append("         │        ├─── 2017 (21 books)")
    lines.append("         │        ├─── 2016 (15 books)")
    lines.append("         │        ├─── 2015 (3 books)")
    lines.append("         │        └─── Prior (77 books)")
    lines.append("         │")
    lines.append("         └─ Epilogue ─── Previous versions (v1, v2, v3)")
    lines.append("")
    lines.append("     PERSONAL WEBSITE & DIGITAL GARDEN")
    lines.append("              TEXT ONLY")

    return "\n".join(lines)

def generate_reading_stats():
    """Generate reading statistics with sparkline"""
    data = load_books_data()

    # Count by year
    books_by_year = {}
    for book in data['books']:
        year = book.get('year')
        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1

    years = sorted(books_by_year.items())
    total = sum(books_by_year.values())
    avg = total / len(books_by_year)

    # Create sparkline
    max_val = max(books_by_year.values())
    sparkline_chars = " ▁▂▃▄▅▆▇█"
    sparkline = ""
    for year, count in years:
        index = int((count / max_val) * (len(sparkline_chars) - 1))
        sparkline += sparkline_chars[index]

    lines = []
    lines.append("READING STATISTICS")
    lines.append("")
    lines.append(f"Total Books (2015-2020): {total}")
    lines.append(f"Average per Year:        {avg:.1f}")
    lines.append(f"Peak Year:               2017 (21 books)")
    lines.append(f"Trend (2015-2020):       {sparkline}")
    lines.append("")
    lines.append("Genre Distribution:")
    lines.append("├─ Fiction:        ~40%")
    lines.append("├─ Non-fiction:    ~35%")
    lines.append("├─ Technical:      ~15%")
    lines.append("└─ Other:          ~10%")

    return "\n".join(lines)

if __name__ == "__main__":
    print("Generating ASCII visualizations...")
    print("\n" + "=" * 70 + "\n")

    print(generate_books_bar_chart())
    print("\n" + "=" * 70 + "\n")

    print(generate_career_timeline())
    print("\n" + "=" * 70 + "\n")

    print(generate_site_tree())
    print("\n" + "=" * 70 + "\n")

    print(generate_reading_stats())
