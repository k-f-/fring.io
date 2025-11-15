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
    """VIZ-BOOKS-HBAR-001: Horizontal bar chart of books read per year"""
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
    """VIZ-CAREER-VERT-001: Vertical career timeline - progression moves upward"""
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
    """VIZ-SITE-TREE-001: Phylogenetic tree structure with clickable links"""
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

# ============================================================================
# BOOKS VISUALIZATIONS - Additional Permutations
# ============================================================================

def generate_books_vertical_bars():
    """VIZ-BOOKS-VBAR-002: Vertical bar chart (rotated 90 degrees)"""
    data = load_books_data()

    # Count books by year
    books_by_year = {}
    prior_books = 0

    for book in data['books']:
        year = book.get('year')
        year_label = book.get('yearLabel')

        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1
        elif year_label:
            prior_books += 1

    years = sorted(books_by_year.items())
    max_books = max(books_by_year.values()) if books_by_year else 1

    lines = []
    lines.append("READING ACTIVITY - Vertical Bars [VIZ-BOOKS-VBAR-002]")
    lines.append("")

    # Create vertical bars (height = 20 rows max)
    for height in range(20, -1, -1):
        row = ""
        for year, count in years:
            bar_height = int((count / max_books) * 20)
            if height <= bar_height:
                row += " █ "
            elif height == 0:
                row += f"{year % 100:02d} "  # Show last 2 digits
            else:
                row += "   "
        lines.append(row)

    # Add counts below
    count_line = ""
    for year, count in years:
        count_line += f"{count:2d} "
    lines.append("    " + count_line)

    return "\n".join(lines)

def generate_books_line_graph():
    """VIZ-BOOKS-LINE-003: Line graph with trend"""
    data = load_books_data()

    # Count books by year
    books_by_year = {}
    for book in data['books']:
        year = book.get('year')
        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1

    years = sorted(books_by_year.items())
    max_books = max(books_by_year.values()) if books_by_year else 1

    lines = []
    lines.append("READING TREND - Line Graph [VIZ-BOOKS-LINE-003]")
    lines.append("")

    # Create line graph (height = 15 rows)
    for height in range(15, -1, -1):
        row = f"{height:2d} │"
        for i, (year, count) in enumerate(years):
            plot_height = int((count / max_books) * 15)

            if plot_height == height:
                # Check if we should draw a line to next point
                if i < len(years) - 1:
                    next_height = int((years[i+1][1] / max_books) * 15)
                    if next_height > plot_height:
                        row += "╱"
                    elif next_height < plot_height:
                        row += "╲"
                    else:
                        row += "─"
                else:
                    row += "●"
            elif i > 0:
                prev_height = int((years[i-1][1] / max_books) * 15)
                if plot_height > height > prev_height or plot_height < height < prev_height:
                    if prev_height < plot_height:
                        row += "╱"
                    else:
                        row += "╲"
                else:
                    row += " "
            else:
                row += " "
        lines.append(row)

    # X-axis
    lines.append("   └" + "─" * len(years))
    axis_line = "    "
    for year, count in years:
        axis_line += str(year)[-2:]
    lines.append(axis_line[:40])

    return "\n".join(lines)

def generate_books_sparkline():
    """VIZ-BOOKS-SPARK-004: Compact sparkline view with stats"""
    data = load_books_data()

    # Count books by year
    books_by_year = {}
    prior_books = 0

    for book in data['books']:
        year = book.get('year')
        year_label = book.get('yearLabel')

        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1
        elif year_label:
            prior_books += 1

    years = sorted(books_by_year.items())
    max_books = max(books_by_year.values()) if books_by_year else 1
    total = sum(books_by_year.values())
    avg = total / len(books_by_year) if books_by_year else 0

    # Create sparklines with different character sets
    sparkline_chars = " ▁▂▃▄▅▆▇█"
    blocks = ""
    dots = ""
    bars = ""

    for year, count in years:
        index = int((count / max_books) * (len(sparkline_chars) - 1))
        blocks += sparkline_chars[index]
        # Dots version
        if count == max_books:
            dots += "●"
        elif count > max_books * 0.66:
            dots += "◉"
        elif count > max_books * 0.33:
            dots += "○"
        else:
            dots += "·"
        # Bars version
        bars += "│" if count > avg else "┆"

    lines = []
    lines.append("READING TRENDS - Sparklines [VIZ-BOOKS-SPARK-004]")
    lines.append("")
    lines.append(f"Total: {total + prior_books} books │ 2015-2020: {total} │ Prior: {prior_books}")
    lines.append(f"Average: {avg:.1f}/year │ Peak: {max_books} books")
    lines.append("")
    lines.append(f"Blocks: {blocks}")
    lines.append(f"Dots:   {dots}")
    lines.append(f"Bars:   {bars}")
    lines.append(f"Years:  {''.join(str(y)[-2:] for y, c in years)}")

    return "\n".join(lines)

def generate_books_dot_plot():
    """VIZ-BOOKS-DOT-005: Dot plot / scatter visualization"""
    data = load_books_data()

    # Count books by year
    books_by_year = {}
    for book in data['books']:
        year = book.get('year')
        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1

    years = sorted(books_by_year.items())
    max_books = max(books_by_year.values()) if books_by_year else 1

    lines = []
    lines.append("READING DISTRIBUTION - Dot Plot [VIZ-BOOKS-DOT-005]")
    lines.append("")

    # Create dot plot
    for height in range(max_books, -1, -1):
        row = f"{height:2d} │"
        for year, count in years:
            if count >= height:
                row += "● "
            else:
                row += "  "
        lines.append(row)

    # X-axis
    lines.append("   └" + "──" * len(years))
    year_labels = "    "
    for year, count in years:
        year_labels += f"{year} "
    lines.append(year_labels[:50])

    return "\n".join(lines)

# ============================================================================
# CAREER VISUALIZATIONS - Additional Permutations
# ============================================================================

def generate_career_horizontal():
    """VIZ-CAREER-HORIZ-002: Horizontal timeline (classic Gantt style)"""
    data = load_career_data()

    lines = []
    lines.append("CAREER TIMELINE - Horizontal [VIZ-CAREER-HORIZ-002]")
    lines.append("")

    # Timeline from 2006 to 2025
    current_year = 2025
    timeline_start = 2006
    timeline_width = 50

    # Year markers
    years_header = "       "
    for year in range(timeline_start, current_year + 1, 5):
        years_header += f"{year}  "
    lines.append(years_header[:timeline_width])
    lines.append("       " + "┬────┬────┬────┬")

    # Plot each role
    for exp in reversed(data['experience']):
        title = exp['title'][:25]
        company = exp.get('company', 'Independent')[:15]
        start = int(exp['startDate'].split('-')[0])
        end = int(exp['endDate'].split('-')[0]) if exp.get('endDate') else current_year

        # Calculate position
        start_pos = int(((start - timeline_start) / (current_year - timeline_start)) * 40)
        end_pos = int(((end - timeline_start) / (current_year - timeline_start)) * 40)
        duration = max(end_pos - start_pos, 1)

        # Create bar
        bar = " " * start_pos + "├" + "─" * (duration - 1)
        if exp.get('current'):
            bar += "►"
        else:
            bar += "┤"

        role_label = f" {title} @ {company}"
        lines.append(bar[:40].ljust(40) + " │" + role_label)

    return "\n".join(lines)

def generate_career_compact():
    """VIZ-CAREER-COMPACT-003: Minimal single-line timeline"""
    data = load_career_data()

    lines = []
    lines.append("CAREER - Compact Timeline [VIZ-CAREER-COMPACT-003]")
    lines.append("")

    # Single line with markers
    timeline = "2006"
    for exp in reversed(data['experience']):
        start = exp['startDate'][:4]
        title_abbr = ''.join([word[0] for word in exp['title'].split()[:3]])
        timeline += f" → {start}:{title_abbr}"

    lines.append(timeline)
    lines.append("")

    # Legend
    lines.append("Legend:")
    for exp in reversed(data['experience']):
        title_abbr = ''.join([word[0] for word in exp['title'].split()[:3]])
        lines.append(f"  {title_abbr} = {exp['title']}")

    return "\n".join(lines)

def generate_career_tree():
    """VIZ-CAREER-TREE-004: Tree/org-chart style by company"""
    data = load_career_data()

    lines = []
    lines.append("CAREER - Organization View [VIZ-CAREER-TREE-004]")
    lines.append("")

    # Group by company
    by_company = {}
    for exp in data['experience']:
        company = exp.get('company', 'Independent')
        if company not in by_company:
            by_company[company] = []
        by_company[company].append(exp)

    # Build tree
    lines.append("CAREER HISTORY")
    for i, (company, roles) in enumerate(by_company.items()):
        is_last_company = (i == len(by_company) - 1)
        prefix = "└── " if is_last_company else "├── "
        lines.append(f"{prefix}{company}")

        for j, role in enumerate(roles):
            is_last_role = (j == len(roles) - 1)
            role_prefix = "    └── " if is_last_company else "│   └── " if is_last_role else "│   ├── "
            if not is_last_company and not is_last_role:
                role_prefix = "│   ├── "
            start = role['startDate'][:4]
            end = role['endDate'][:4] if role.get('endDate') else 'Present'
            lines.append(f"{role_prefix}{role['title']} ({start}-{end})")

    return "\n".join(lines)

# ============================================================================
# SITE STRUCTURE VISUALIZATIONS - Additional Permutations
# ============================================================================

def generate_site_indent():
    """VIZ-SITE-INDENT-002: Simple indented list with Unicode"""
    lines = []
    lines.append("SITE MAP - Indented [VIZ-SITE-INDENT-002]")
    lines.append("")
    lines.append("□ fring.io")
    lines.append("  ├─ <a href=\"#now\">Now</a>")
    lines.append("  │  ├─ Life (Chattanooga, TN)")
    lines.append("  │  ├─ Work (Program Director)")
    lines.append("  │  └─ Future (Career goals)")
    lines.append("  ├─ <a href=\"#visualizations\">Data</a> (Visualizations)")
    lines.append("  ├─ <a href=\"#elsewhere\">Elsewhere</a> (GitHub, LinkedIn, Goodreads)")
    lines.append("  ├─ <a href=\"#bookshelf\">Bookshelf</a>")
    lines.append("  │  ├─ 2020 (9 books)")
    lines.append("  │  ├─ 2019 (6 books)")
    lines.append("  │  ├─ 2018 (12 books)")
    lines.append("  │  ├─ 2017 (21 books)")
    lines.append("  │  ├─ 2016 (15 books)")
    lines.append("  │  ├─ 2015 (3 books)")
    lines.append("  │  └─ Prior (77 books)")
    lines.append("  └─ <a href=\"#epilogue\">Epilogue</a> (v1, v2, v3)")

    return "\n".join(lines)

def generate_site_boxes():
    """VIZ-SITE-BOXES-003: Box/card style layout"""
    lines = []
    lines.append("SITE NAVIGATION - Boxes [VIZ-SITE-BOXES-003]")
    lines.append("")
    lines.append("┌─────────────┬─────────────┬─────────────┬─────────────┐")
    lines.append("│ <a href=\"#now\">NOW</a>        │ <a href=\"#visualizations\">DATA</a>       │ <a href=\"#elsewhere\">ELSEWHERE</a>  │ <a href=\"#bookshelf\">BOOKS</a>      │")
    lines.append("│             │             │             │             │")
    lines.append("│ Life        │ Charts      │ GitHub      │ 143 books   │")
    lines.append("│ Work        │ Graphs      │ LinkedIn    │ 2015-2020   │")
    lines.append("│ Future      │ Stats       │ Goodreads   │ + Prior     │")
    lines.append("└─────────────┴─────────────┴─────────────┴─────────────┘")

    return "\n".join(lines)

# ============================================================================
# NEW DATA VISUALIZATIONS
# ============================================================================

def generate_tech_stack():
    """VIZ-TECH-STACK-001: Technology skills timeline from career.json"""
    data = load_career_data()

    lines = []
    lines.append("TECHNOLOGY STACK - Timeline [VIZ-TECH-STACK-001]")
    lines.append("")

    # Extract tech from currentStack
    if 'summary' in data and 'currentStack' in data['summary']:
        stack = data['summary']['currentStack']

        lines.append("Current Tech Stack:")
        lines.append("")

        for category, items in stack.items():
            lines.append(f"  {category.upper()}:")
            for item in items:
                lines.append(f"    ▪ {item}")

        lines.append("")
        lines.append("Experience Timeline:")
        lines.append("2006 ━━━━━━━━━━━━━━━ Network Engineering")
        lines.append("2008 ━━━━━━━━━━━━━━━ Systems Administration")
        lines.append("2012 ━━━━━━━━━━━━━━━ AWS & Cloud")
        lines.append("2015 ━━━━━━━━━━━━━━━ DevOps")
        lines.append("2020 ━━━━━━━━━━━━━━━ Data Engineering ◄── Current Focus")
        lines.append("2023 ━━━━━━━━━━━━━━━ AI/ML & Analytics")

    return "\n".join(lines)

def generate_reading_velocity():
    """VIZ-READING-VEL-001: Reading velocity/pace over time"""
    data = load_books_data()

    # Calculate books per year
    books_by_year = {}
    for book in data['books']:
        year = book.get('year')
        if isinstance(year, int):
            books_by_year[year] = books_by_year.get(year, 0) + 1

    years = sorted(books_by_year.items())

    lines = []
    lines.append("READING VELOCITY - Pace Analysis [VIZ-READING-VEL-001]")
    lines.append("")

    # Show pace indicators
    avg = sum(books_by_year.values()) / len(books_by_year) if books_by_year else 0

    for year, count in years:
        pace_indicator = ""
        if count > avg * 1.5:
            pace_indicator = "▲▲▲ High pace"
            bar = "█" * 20
        elif count > avg:
            pace_indicator = "▲▲  Above avg"
            bar = "▓" * 15
        elif count < avg * 0.5:
            pace_indicator = "▼▼▼ Slow pace"
            bar = "░" * 5
        else:
            pace_indicator = "▼   Below avg"
            bar = "▒" * 10

        lines.append(f"{year}: {bar} {count:2d} books {pace_indicator}")

    lines.append("")
    lines.append(f"Average pace: {avg:.1f} books/year")

    return "\n".join(lines)

def generate_decade_distribution():
    """VIZ-DECADE-DIST-001: Books distribution by decade"""
    data = load_books_data()

    # This is a conceptual visualization showing distribution
    # Since we don't have publication dates, we'll show reading decades

    lines = []
    lines.append("READING DISTRIBUTION - By Decade [VIZ-DECADE-DIST-001]")
    lines.append("")
    lines.append("┌─────────────────────────────────────────────┐")
    lines.append("│ 2010s (2015-2020): 66 books  ████████░░     │")
    lines.append("│ Pre-2015:          77 books  ██████████     │")
    lines.append("├─────────────────────────────────────────────┤")
    lines.append("│ Total Tracked:     143 books                │")
    lines.append("│ Reading Period:    ~10+ years               │")
    lines.append("│ Rate:              ~14 books/year           │")
    lines.append("└─────────────────────────────────────────────┘")
    lines.append("")
    lines.append("Reading Era Analysis:")
    lines.append("  2015-2017 ████████ Peak reading phase (36 books)")
    lines.append("  2018-2020 ███░░░░░ Sustained reading (27 books)")
    lines.append("  Pre-2015  ██████░░ Historical collection (77 books)")

    return "\n".join(lines)

if __name__ == "__main__":
    print("Generating ASCII visualizations...")
    print("\n" + "=" * 70 + "\n")

    # Original visualizations
    print(generate_books_bar_chart())
    print("\n" + "=" * 70 + "\n")

    print(generate_career_timeline())
    print("\n" + "=" * 70 + "\n")

    print(generate_site_tree())
    print("\n" + "=" * 70 + "\n")

    # Books permutations
    print(generate_books_vertical_bars())
    print("\n" + "=" * 70 + "\n")

    print(generate_books_line_graph())
    print("\n" + "=" * 70 + "\n")

    print(generate_books_sparkline())
    print("\n" + "=" * 70 + "\n")

    print(generate_books_dot_plot())
    print("\n" + "=" * 70 + "\n")

    # Career permutations
    print(generate_career_horizontal())
    print("\n" + "=" * 70 + "\n")

    print(generate_career_compact())
    print("\n" + "=" * 70 + "\n")

    print(generate_career_tree())
    print("\n" + "=" * 70 + "\n")

    # Site structure permutations
    print(generate_site_indent())
    print("\n" + "=" * 70 + "\n")

    print(generate_site_boxes())
    print("\n" + "=" * 70 + "\n")

    # New data visualizations
    print(generate_tech_stack())
    print("\n" + "=" * 70 + "\n")

    print(generate_reading_velocity())
    print("\n" + "=" * 70 + "\n")

    print(generate_decade_distribution())
