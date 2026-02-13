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

def load_albums_data():
    """Load and parse albums.json"""
    with open('../../content/albums.json', 'r') as f:
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

    # Each data point occupies 3 characters for proper spacing
    spacing = 3

    # Create line graph (height = 15 rows)
    for height in range(15, -1, -1):
        row = f"{height:2d} │"

        for i, (year, count) in enumerate(years):
            plot_height = int((count / max_books) * 15)

            if plot_height == height:
                # At a data point
                if i < len(years) - 1:
                    next_height = int((years[i+1][1] / max_books) * 15)
                    if next_height > plot_height:
                        row += "╱  "
                    elif next_height < plot_height:
                        row += "╲  "
                    else:
                        row += "─  "
                else:
                    row += "●  "
            elif i > 0:
                # Between points - draw connector
                prev_height = int((years[i-1][1] / max_books) * 15)
                curr_height = plot_height

                # Check if we're on the line between previous and current point
                if (prev_height < curr_height and prev_height < height < curr_height) or \
                   (prev_height > curr_height and curr_height < height < prev_height):
                    if prev_height < curr_height:
                        row += "╱  "
                    else:
                        row += "╲  "
                else:
                    row += "   "
            else:
                row += "   "

        lines.append(row.rstrip())

    # X-axis
    axis_width = len(years) * spacing
    lines.append("   └" + "─" * axis_width)

    # Year labels
    axis_line = "    "
    for year, count in years:
        axis_line += f"{str(year)[-2:]} "
    lines.append(axis_line.rstrip())

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

    # Plot each role (newest first)
    for exp in data['experience']:
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
    lines.append("  │  ├─ Life (<a href=\"https://en.wikipedia.org/wiki/Chattanooga,_Tennessee\">Chattanooga, TN</a>)")
    lines.append("  │  ├─ Work (Program Director)")
    lines.append("  │  └─ Future (Career goals)")
    lines.append("  ├─ <a href=\"#visualizations\">Data</a> (Visualizations)")
    lines.append("  ├─ <a href=\"#elsewhere\">Elsewhere</a> (GitHub, LinkedIn, Goodreads)")
    lines.append("  ├─ <a href=\"#bookshelf\">Bookshelf</a>")
    lines.append("  │  ├─ <a href=\"#b2020\">2020</a> (9 books)")
    lines.append("  │  ├─ <a href=\"#b2019\">2019</a> (6 books)")
    lines.append("  │  ├─ <a href=\"#b2018\">2018</a> (12 books)")
    lines.append("  │  ├─ <a href=\"#b2017\">2017</a> (21 books)")
    lines.append("  │  ├─ <a href=\"#b2016\">2016</a> (15 books)")
    lines.append("  │  ├─ <a href=\"#b2015\">2015</a> (3 books)")
    lines.append("  │  └─ <a href=\"#bprior\">Prior</a> (77 books)")
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

def generate_reading_calendar():
    """VIZ-READING-CAL-001: GitHub-style calendar heatmap of reading activity"""
    data = load_books_data()
    from datetime import datetime, timedelta
    from collections import defaultdict
    import random

    # Count books by year (use year field, not dateAdded)
    books_by_year = defaultdict(list)

    for book in data['books']:
        year = book.get('year')
        if isinstance(year, int) and 2015 <= year <= 2020:
            books_by_year[year].append(book)

    if not books_by_year:
        return "READING CALENDAR [VIZ-READING-CAL-001]\n(No year data available)"

    # Use most recent year with data or a representative year
    # For visualization purposes, we'll show 2017 (peak year)
    target_year = 2017
    if target_year not in books_by_year:
        target_year = max(books_by_year.keys())

    # Create calendar grid for the target year
    lines = []
    lines.append("READING CALENDAR - Activity Heatmap [VIZ-READING-CAL-001]")
    lines.append(f"Reading activity for {target_year} ({len(books_by_year[target_year])} books)")
    lines.append("")

    # Distribute books across weeks (simulated, since we don't have exact dates)
    # Create a more realistic spread across the year
    books_by_week = defaultdict(int)
    random.seed(target_year)  # Deterministic distribution

    for book in books_by_year[target_year]:
        # Random week in the year (1-52)
        week = random.randint(1, 52)
        books_by_week[week] += 1

    # Month labels
    start_date = datetime(target_year, 1, 1)
    month_labels = "     "

    for week in range(52):
        week_date = start_date + timedelta(weeks=week)
        if week % 4 == 0:  # Every 4 weeks
            month_labels += week_date.strftime('%b')[:3] + " "
        else:
            month_labels += "    "

    lines.append(month_labels)

    # Days of week (show Mon, Wed, Fri, Sun for compactness)
    days = ['Mon', 'Wed', 'Fri', 'Sun']

    for day_idx in range(4):
        line = f"{days[day_idx]:3s}  "

        for week in range(1, 53):
            count = books_by_week.get(week, 0)

            # Choose character based on intensity
            if count == 0:
                char = "·"
            elif count == 1:
                char = "░"
            elif count == 2:
                char = "▒"
            elif count == 3:
                char = "▓"
            else:
                char = "█"

            line += char + " "

        lines.append(line)

    lines.append("")
    lines.append("Legend: · None  ░ 1 book  ▒ 2 books  ▓ 3 books  █ 4+ books")
    lines.append(f"Note: Distribution is simulated based on yearly totals")

    return "\n".join(lines)

def generate_location_roadways():
    """VIZ-LOCATION-ROAD-001: Chattanooga highway intersection diagram"""
    lines = []
    lines.append("CHATTANOOGA ROADWAYS - Compass Layout [VIZ-LOCATION-ROAD-001]")
    lines.append("")
    lines.append("                        N")
    lines.append("                        ↑")
    lines.append("")
    lines.append("        Nashville          Knoxville")
    lines.append("         (134 mi)           (112 mi)")
    lines.append("            NW                  NE")
    lines.append("              ↖               ↗")
    lines.append("             I-24           I-75")
    lines.append("                ╲         ╱")
    lines.append("                 ╲       ╱")
    lines.append("                  ╲     ╱")
    lines.append("        W ←────── CHATTANOOGA ──────→ E")
    lines.append("                  ╱     ╲")
    lines.append("                 ╱       ╲")
    lines.append("                ╱         ╲")
    lines.append("             I-59          I-75")
    lines.append("              ↙               ↘")
    lines.append("            WSW               SSE")
    lines.append("        Birmingham          Atlanta")
    lines.append("         (147 mi)          (118 mi)")
    lines.append("")
    lines.append("                        ↓")
    lines.append("                        S")
    lines.append("")
    lines.append("Interstate Corridors:")
    lines.append("  I-75: NE-SW spine (Detroit ↔ Miami)")
    lines.append("  I-24: NW-SE connector (Nashville ↔ Chattanooga → Georgia)")
    lines.append("  I-59: WSW branch (Chattanooga ← Birmingham ↔ New Orleans)")
    lines.append("")
    lines.append("Geographic Hub: 80% pass-through freight traffic")
    lines.append("Coordinates: 35.05°N, 85.31°W 📍")

    return "\n".join(lines)

# ============================================================================
# ALBUMS VISUALIZATIONS
# ============================================================================

def parse_playtime(playtime_str):
    """Parse playtime string to minutes (e.g., '2 hr 13 min.' -> 133)"""
    if not playtime_str:
        return 0

    minutes = 0
    # Handle various formats: "2 hr 13 min.", "34 min.", "41 min", "38 minutes.", "61 Minutes"
    parts = playtime_str.lower().replace('.', '').split()

    i = 0
    while i < len(parts):
        if parts[i].isdigit():
            num = int(parts[i])
            if i + 1 < len(parts):
                unit = parts[i + 1]
                if 'hr' in unit or 'hour' in unit:
                    minutes += num * 60
                elif 'min' in unit:
                    minutes += num
            i += 2
        else:
            i += 1

    return minutes

def generate_albums_artist_freq():
    """VIZ-ALBUMS-ARTIST-001: Artist frequency dot plot (compact)"""
    data = load_albums_data()

    # Count albums by artist
    artist_counts = {}
    for album in data['albums']:
        artist = album['artist']
        artist_counts[artist] = artist_counts.get(artist, 0) + 1

    # Sort by count descending, then alphabetically
    artists = sorted(artist_counts.items(), key=lambda x: (-x[1], x[0]))

    # Only show artists with more than 1 album, or top 10
    significant_artists = [a for a in artists if a[1] > 1]
    if not significant_artists:
        significant_artists = artists[:10]

    max_count = max(artist_counts.values())
    total_albums = len(data['albums'])
    unique_artists = len(artist_counts)

    lines = []
    lines.append("ALBUM ARTISTS - Frequency Analysis [VIZ-ALBUMS-ARTIST-001]")
    lines.append("")
    lines.append(f"Total: {total_albums} albums │ Artists: {unique_artists} │ Avg: {total_albums/unique_artists:.1f} albums/artist")
    lines.append("")

    # Show artist frequencies
    for artist, count in significant_artists:
        dots = "●" * count + "○" * (max_count - count)
        lines.append(f"{artist[:30]:30s} │{dots} {count}")

    lines.append("")
    lines.append(f"Showing artists with 2+ albums ({len(significant_artists)} of {unique_artists})")

    return "\n".join(lines)

def generate_albums_artist_sparkline():
    """VIZ-ALBUMS-ARTIST-002: Artist listening patterns over time"""
    data = load_albums_data()

    # Count albums by artist
    artist_counts = {}
    for album in data['albums']:
        artist = album['artist']
        artist_counts[artist] = artist_counts.get(artist, 0) + 1

    # Find artists with multiple albums
    multi_album_artists = [a for a, c in artist_counts.items() if c > 1]

    lines = []
    lines.append("ARTIST PATTERNS - Sparkline View [VIZ-ALBUMS-ARTIST-002]")
    lines.append("")

    if multi_album_artists:
        for artist in multi_album_artists:
            count = artist_counts[artist]
            sparkline = "█" * count + "░" * (5 - count)
            lines.append(f"{artist[:25]:25s} {sparkline[:5]} ({count} albums)")
    else:
        lines.append("All albums by different artists - diverse listening!")

    lines.append("")
    lines.append(f"Diversity Index: {len(artist_counts)}/{len(data['albums'])} = {len(artist_counts)/len(data['albums']):.1%}")

    return "\n".join(lines)

def generate_albums_decade_dist():
    """VIZ-ALBUMS-YEAR-001: Decade distribution histogram (compact)"""
    data = load_albums_data()

    # Group by decade
    decade_counts = {}
    for album in data['albums']:
        year = album['releaseYear']
        decade = (year // 10) * 10
        decade_counts[decade] = decade_counts.get(decade, 0) + 1

    decades = sorted(decade_counts.items())
    max_count = max(decade_counts.values())

    lines = []
    lines.append("ALBUM RELEASE DECADES - Distribution [VIZ-ALBUMS-YEAR-001]")
    lines.append("")

    # Create histogram
    for decade, count in decades:
        bar_length = int((count / max_count) * 30)
        bar = "█" * bar_length
        decade_label = f"{decade}s"
        lines.append(f"{decade_label:6s} │{bar:30s} {count:2d}")

    lines.append("       └" + "─" * 35)

    # Add sparkline
    sparkline_chars = " ▁▂▃▄▅▆▇█"
    sparkline = ""
    for decade, count in decades:
        index = int((count / max_count) * (len(sparkline_chars) - 1))
        sparkline += sparkline_chars[index]

    lines.append("")
    lines.append(f"Trend: {sparkline}")
    lines.append(f"Decades: {''.join(str(d)[-2:] for d, c in decades)}")

    return "\n".join(lines)

def generate_albums_year_timeline():
    """VIZ-ALBUMS-YEAR-002: Release year vs listen date scatter"""
    data = load_albums_data()

    lines = []
    lines.append("ALBUM TIMELINE - Release Year Analysis [VIZ-ALBUMS-YEAR-002]")
    lines.append("")

    # Get release year range
    release_years = [a['releaseYear'] for a in data['albums']]
    min_year = min(release_years)
    max_year = max(release_years)
    year_range = max_year - min_year

    # Create timeline showing release years
    lines.append(f"Release Year Span: {min_year} → {max_year} ({year_range} years)")
    lines.append("")

    # Group albums by release year
    by_year = {}
    for album in data['albums']:
        year = album['releaseYear']
        by_year[year] = by_year.get(year, 0) + 1

    # Create compact dot plot for timeline
    lines.append("Release Timeline:")
    for year in sorted(by_year.keys()):
        count = by_year[year]
        dots = "●" * count
        lines.append(f"{year} │{dots}")

    # Calculate age statistics
    listen_year = 2019  # All albums listened in 2019
    ages = [listen_year - y for y in release_years]
    avg_age = sum(ages) / len(ages)
    oldest = max(ages)
    newest = min(ages)

    lines.append("")
    lines.append(f"Album Age When Listened (2019):")
    lines.append(f"  Oldest:  {oldest} years ({min_year})")
    lines.append(f"  Newest:  {newest} years ({max_year})")
    lines.append(f"  Average: {avg_age:.1f} years")

    return "\n".join(lines)

def generate_albums_track_distribution():
    """VIZ-ALBUMS-CHARS-001: Track count distribution sparkline"""
    data = load_albums_data()

    # Get track counts
    track_counts = [a['tracks'] for a in data['albums']]
    min_tracks = min(track_counts)
    max_tracks = max(track_counts)
    avg_tracks = sum(track_counts) / len(track_counts)

    # Create distribution
    track_dist = {}
    for count in track_counts:
        track_dist[count] = track_dist.get(count, 0) + 1

    lines = []
    lines.append("TRACK COUNT DISTRIBUTION - Compact View [VIZ-ALBUMS-CHARS-001]")
    lines.append("")
    lines.append(f"Range: {min_tracks}-{max_tracks} tracks │ Avg: {avg_tracks:.1f} │ Median: {sorted(track_counts)[len(track_counts)//2]}")
    lines.append("")

    # Show distribution with dots
    for tracks in sorted(track_dist.keys()):
        count = track_dist[tracks]
        dots = "●" * count
        lines.append(f"{tracks:2d} tracks │{dots} ({count} albums)")

    # Find most common
    most_common_tracks = max(track_dist.items(), key=lambda x: x[1])
    lines.append("")
    lines.append(f"Most common: {most_common_tracks[0]} tracks ({most_common_tracks[1]} albums)")

    return "\n".join(lines)

def generate_albums_playtime_scatter():
    """VIZ-ALBUMS-CHARS-002: Playtime vs tracks scatter plot"""
    data = load_albums_data()

    lines = []
    lines.append("ALBUM CHARACTERISTICS - Duration vs Tracks [VIZ-ALBUMS-CHARS-002]")
    lines.append("")

    # Parse playtime and create scatter data
    scatter_data = []
    for album in data['albums']:
        tracks = album['tracks']
        minutes = parse_playtime(album.get('playtime', ''))
        if minutes > 0:
            scatter_data.append((tracks, minutes, album['artist'][:20]))

    # Create scatter plot
    max_tracks = max(d[0] for d in scatter_data)
    max_minutes = max(d[1] for d in scatter_data)

    # Grid: 15 rows (minutes), varying columns (tracks)
    lines.append(f"Minutes │")
    for row in range(15, -1, -1):
        minute_threshold = int((row / 15) * max_minutes)
        line = f"{minute_threshold:3d}    │"

        for col in range(0, max_tracks + 1, 4):
            # Check if any album falls in this cell
            has_point = any(
                col <= d[0] < col + 4 and
                minute_threshold - 10 <= d[1] < minute_threshold + 10
                for d in scatter_data
            )
            line += "● " if has_point else "· "

        lines.append(line)

    lines.append("       └" + "─" * 20)
    lines.append("        0   10   20   30   40+ tracks")

    # Statistics
    avg_duration = sum(d[1] for d in scatter_data) / len(scatter_data)
    avg_tracks = sum(d[0] for d in scatter_data) / len(scatter_data)

    lines.append("")
    lines.append(f"Avg duration: {avg_duration:.0f} min │ Avg tracks: {avg_tracks:.1f}")

    return "\n".join(lines)

def generate_albums_duration_dist():
    """VIZ-ALBUMS-CHARS-003: Duration distribution histogram"""
    data = load_albums_data()

    lines = []
    lines.append("ALBUM DURATION DISTRIBUTION [VIZ-ALBUMS-CHARS-003]")
    lines.append("")

    # Parse all playtimes
    durations = []
    for album in data['albums']:
        minutes = parse_playtime(album.get('playtime', ''))
        if minutes > 0:
            durations.append(minutes)

    if not durations:
        return "\n".join(["No duration data available"])

    # Create bins: 0-30, 30-40, 40-50, 50-60, 60+
    bins = {
        '0-30 min': 0,
        '30-40 min': 0,
        '40-50 min': 0,
        '50-60 min': 0,
        '60+ min': 0
    }

    for duration in durations:
        if duration < 30:
            bins['0-30 min'] += 1
        elif duration < 40:
            bins['30-40 min'] += 1
        elif duration < 50:
            bins['40-50 min'] += 1
        elif duration < 60:
            bins['50-60 min'] += 1
        else:
            bins['60+ min'] += 1

    max_count = max(bins.values())

    # Create histogram
    for bin_label, count in bins.items():
        bar_length = int((count / max_count) * 25) if count > 0 else 0
        bar = "█" * bar_length
        lines.append(f"{bin_label:11s} │{bar:25s} {count}")

    lines.append("            └" + "─" * 30)

    # Statistics
    avg_duration = sum(durations) / len(durations)
    min_duration = min(durations)
    max_duration = max(durations)

    lines.append("")
    lines.append(f"Avg: {avg_duration:.0f} min │ Range: {min_duration}-{max_duration} min")

    return "\n".join(lines)

def generate_albums_cover_grid():
    """VIZ-ALBUMS-COVER-001: Album grid with actual cover images"""
    data = load_albums_data()

    # Generate HTML for album cover grid
    albums = data['albums']

    html_parts = []

    # Show all albums in a grid
    for album in albums:
        thumbnail_url = album.get('thumbnailUrl', '')
        spotify_url = album.get('spotifyUrl', '')
        artist = album['artist']
        album_name = album['album']
        year = album['releaseYear']

        # Create clickable album cover
        html_parts.append(
            f'<a href="{spotify_url}" target="_blank" rel="noopener" class="album-cover" '
            f'title="{artist} - {album_name} ({year})">'
            f'<img src="{thumbnail_url}" alt="{artist} - {album_name}" loading="lazy" />'
            f'</a>'
        )

    return '\n'.join(html_parts)

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
    print("\n" + "=" * 70 + "\n")

    print(generate_reading_calendar())
    print("\n" + "=" * 70 + "\n")

    print(generate_location_roadways())
    print("\n" + "=" * 70 + "\n")

    # Albums visualizations
    print(generate_albums_artist_freq())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_artist_sparkline())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_decade_dist())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_year_timeline())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_track_distribution())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_playtime_scatter())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_duration_dist())
    print("\n" + "=" * 70 + "\n")

    print(generate_albums_cover_grid())
