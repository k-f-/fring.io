#!/usr/bin/env python3
"""
regenerate_v4_html.py - Regenerate sites/v4/index.html from content JSON files.

Reads from:
  - content/books.json
  - content/albums.json
  - content/now.json

Generates a single-page HTML file with:
  - Now section (from now.json)
  - Bookshelf section (year-grouped grid from books.json)
  - Albums section (release-year-grouped grid from albums.json)
  - Header icons (from now.json links)
  - Epilogue (static)

Usage:
    python infrastructure/regenerate_v4_html.py
    python infrastructure/regenerate_v4_html.py --preview
"""

import json
import html
import argparse
from datetime import datetime
from pathlib import Path
from collections import OrderedDict


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def format_content_date(date_str: str) -> str:
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return d.strftime("%B %d, %Y")
    except ValueError:
        return date_str


def group_books_by_year(books: list) -> OrderedDict:
    """Group books by year, maintaining order (newest first). yearLabel books go last."""
    groups = OrderedDict()
    for book in books:
        key = book.get("yearLabel") or str(book.get("year", "Unknown"))
        if key not in groups:
            groups[key] = []
        groups[key].append(book["title"])
    return groups


def build_year_sparkline(year_counts: OrderedDict) -> str:
    """Build a year-by-year bar sparkline from an OrderedDict of {year: count}."""
    blocks = " ▁▂▃▄▅▆█"
    max_count = max(year_counts.values()) if year_counts else 1
    parts = []
    for year, count in year_counts.items():
        if count == 0:
            parts.append(f"{year} {blocks[0]}")
        else:
            level = max(1, round(count / max_count * (len(blocks) - 1)))
            parts.append(f"{year} {blocks[level]}")
    return " | ".join(parts)


def generate_book_groups_html(books: list, indent: str = "                ") -> str:
    """Generate book-grid HTML from books list."""
    groups = group_books_by_year(books)
    total = len(books)
    years = [k for k in groups if k != "<2015"]
    year_range = f"{min(years)}–{max(years)}" if years else ""
    if "<2015" in groups:
        year_range += " + prior"

    year_counts = OrderedDict((k, len(v)) for k, v in groups.items())
    sparkline = build_year_sparkline(year_counts)

    lines = []
    lines.append(
        f'{indent}<p class="muted small">{total} books tracked · {year_range}</p>'
    )
    lines.append(f'{indent}<div class="sparkline" aria-hidden="true">')
    lines.append(f"{indent}    {sparkline}")
    lines.append(f"{indent}</div>")
    lines.append(f'{indent}<div class="book-grid">')

    for year_key, titles in groups.items():
        year_display = html.escape(str(year_key))
        lines.append(f'{indent}<div class="book-group">')
        lines.append(f'{indent}    <span class="book-year">{year_display}</span>')
        for title in titles:
            lines.append(
                f'{indent}    <span class="book-title">{html.escape(title)}</span>'
            )
        lines.append(f"{indent}</div>")

    lines.append(f"{indent}</div>")
    return "\n".join(lines)


def group_albums_by_year(albums: list) -> OrderedDict:
    """Group albums by listened year, newest first."""
    sorted_albums = sorted(
        albums, key=lambda a: a.get("listenedDate", ""), reverse=True
    )
    groups = OrderedDict()
    for album in sorted_albums:
        year = album.get("listenedDate", "")[:4] or "Unknown"
        if year not in groups:
            groups[year] = []
        groups[year].append(album)
    return groups


def generate_albums_html(albums: list, indent: str = "                ") -> str:
    """Generate year-grouped album grid HTML, sorted by listened date (newest first)."""
    groups = group_albums_by_year(albums)
    total = len(albums)

    release_years = [a.get("releaseYear") for a in albums if a.get("releaseYear")]
    year_span = f"{min(release_years)}–{max(release_years)}" if release_years else ""

    year_counts = OrderedDict((k, len(v)) for k, v in groups.items())
    sparkline = build_year_sparkline(year_counts)

    lines = []
    lines.append(
        f'{indent}<p class="muted small">{total} albums · releases spanning {year_span}</p>'
    )
    lines.append(f'{indent}<div class="sparkline" aria-hidden="true">')
    lines.append(f"{indent}    {sparkline}")
    lines.append(f"{indent}</div>")
    lines.append(f'{indent}<div class="album-grid">')

    for year, year_albums in groups.items():
        lines.append(f'{indent}<div class="album-group">')
        lines.append(f'{indent}    <span class="album-year">{html.escape(year)}</span>')

        for album in year_albums:
            artist = html.escape(album["artist"])
            name = html.escape(album["album"])
            release_year = album.get("releaseYear", "")
            title_text = f"{artist} — {name}"
            if release_year:
                title_text += f" ({release_year})"

            spotify_url = album.get("spotifyUrl")
            if spotify_url:
                lines.append(
                    f'{indent}    <a href="{html.escape(spotify_url)}" target="_blank" class="album-title">{title_text}</a>'
                )
            else:
                lines.append(
                    f'{indent}    <span class="album-title">{title_text}</span>'
                )

            if album.get("notes"):
                lines.append(
                    f'{indent}    <span class="album-note">{html.escape(album["notes"])}</span>'
                )

        lines.append(f"{indent}</div>")

    lines.append(f"{indent}</div>")
    return "\n".join(lines)


def generate_now_html(now: dict, indent: str = "                ") -> str:
    """Generate Now section content from now.json."""
    sections = now["sections"]
    location = now["location"]

    life_text = sections["life"]["text"]
    life_paragraphs = life_text.split("\n\n")
    crux_url = sections["life"]["highlights"][0]["url"]

    work = sections["work"]
    future = sections["future"]["desires"]

    lines = []
    lines.append(f"{indent}<h3>Life</h3>")
    lines.append(
        f'{indent}<aside class="muted">{location["emoji"]} {location["city"]}, {location["state"]}</aside>'
    )
    for p in life_paragraphs:
        p_html = p.replace("Crux", f'<a href="{crux_url}">Crux</a>')
        p_html = p_html.replace("ultra", "<em>ultra</em>")
        lines.append(f"{indent}<p>{p_html}</p>")

    lines.append(f"{indent}<h3>Work</h3>")
    role = work["currentRole"]
    company = work["company"]
    desc = work["description"]
    lines.append(
        f"{indent}<p>I'm fortunate to be able to work remotely as a <strong>{role}</strong> for a {company}. {desc}</p>"
    )

    lines.append(f"{indent}<h3>Future</h3>")
    lines.append(f"{indent}<ul>")
    for desire in future:
        d = desire
        d = d.replace("very", "<em>very</em>")
        d = d.replace("FOSS", "<em>FOSS</em>")
        d = d.replace("specialization", "<em>specialization</em>")
        d = d.replace("not", "<em>not</em>")
        d = d.replace("way", "<strong>way</strong>")
        lines.append(f"{indent}    <li>{d}</li>")
    lines.append(f"{indent}</ul>")

    return "\n".join(lines)


ICON_GITHUB = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>'

ICON_LINKEDIN = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>'

ICON_GOODREADS = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M11.43 23.995c-3.608-.208-6.274-2.077-6.448-5.078.695.007 1.375-.013 2.07-.006.224 1.342 1.065 2.43 2.683 3.026 1.583.496 3.737.46 5.082-.174 1.351-.636 2.145-1.822 2.503-3.577.212-1.042.236-1.734.231-2.92l-.005-1.199h-.046c-.556 1.118-1.278 2.003-2.27 2.622-1.063.665-2.307.96-3.525.96-2.605 0-4.403-1.395-5.505-3.397-.93-1.686-1.327-3.97-1.174-6.21.096-1.417.39-2.725.936-3.856.547-1.13 1.347-2.08 2.374-2.755.969-.638 2.148-1.015 3.483-1.015 1.211 0 2.278.272 3.167.837.89.564 1.571 1.39 2.126 2.405h.044l.179-2.935h2.003c-.042.554-.08 1.388-.08 2.495l-.004 11.237c.002 2.467-.236 4.287-.882 5.578-.872 1.722-2.736 3.072-5.543 3.072-.553 0-1.082-.044-1.6-.11zm3.57-8.236c1.02-.627 1.737-1.558 2.145-2.659.365-.983.494-2.221.494-3.545 0-1.254-.174-2.38-.521-3.386-.403-1.165-1.108-2.083-2.168-2.704-.682-.398-1.456-.6-2.349-.6-1.218 0-2.183.388-2.961 1.158-.749.744-1.263 1.705-1.511 2.892-.192.92-.26 1.853-.217 2.784.05 1.076.231 2.084.597 2.975.464 1.13 1.201 2.028 2.237 2.623.697.399 1.47.596 2.334.596.675 0 1.316-.105 1.92-.334z"/></svg>'


def generate_header_icons_html(now: dict) -> str:
    """Generate inline SVG icon links for the header."""
    links = now["links"]
    icons = []
    if "github" in links:
        icons.append(
            f'<a href="https://github.com/{links["github"]}/" class="header-icon" aria-label="GitHub">{ICON_GITHUB}</a>'
        )
    if "linkedin" in links:
        icons.append(
            f'<a href="https://linkedin.com/in/{links["linkedin"]}/" class="header-icon" aria-label="LinkedIn">{ICON_LINKEDIN}</a>'
        )
    if "goodreads" in links:
        icons.append(
            f'<a href="https://goodreads.com/{links["goodreads"]}/" class="header-icon" aria-label="Goodreads">{ICON_GOODREADS}</a>'
        )
    return "\n            ".join(icons)


def generate_full_html(books_data: dict, albums_data: dict, now_data: dict) -> str:
    """Generate the complete v4 HTML page."""
    books_html = generate_book_groups_html(books_data["books"])
    albums_html = generate_albums_html(albums_data["albums"])
    now_html = generate_now_html(now_data)
    header_icons = generate_header_icons_html(now_data)

    now_content_date = format_content_date(now_data["meta"].get("contentUpdated", ""))
    build_date = datetime.now().strftime("%B %d, %Y")

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kyle Fring</title>
    <meta name="description" content="Kyle Fring — Program Director / Data Engineer. Personal website.">
    <meta property="og:title" content="Kyle Fring">
    <meta property="og:description" content="Program Director / Data Engineer in Chattanooga, TN.">
    <meta property="og:type" content="website">
    
    <style>
        :root {{
            /* Dark Mode (Default) */
            --bg: #1a1a1a;
            --text: #e0e0e0;
            --muted: #888;
            --accent: #5eead4;
            --border: #333;
            --code-bg: #222;
            --selection: rgba(94, 234, 212, 0.2);
            --font-stack: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
        }}

        [data-theme="light"] {{
            --bg: #fafafa;
            --text: #1a1a1a;
            --muted: #666;
            --accent: #0d9488;
            --border: #ddd;
            --code-bg: #f0f0f0;
            --selection: rgba(13, 148, 136, 0.2);
        }}

        * {{
            box-sizing: border-box;
        }}

        ::selection {{
            background: var(--selection);
            color: inherit;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            background-color: var(--bg);
            color: var(--text);
            font-family: var(--font-stack);
            font-size: 16px;
            line-height: 1.7;
            margin: 0;
            padding: 2rem;
            transition: background-color 0.3s ease, color 0.3s ease;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}

        /* Typography */
        h1, h2, h3 {{
            font-weight: 700;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        h1 {{ font-size: 2rem; margin-top: 0; }}
        h2 {{ font-size: 1.4rem; color: var(--accent); }}
        h3 {{ font-size: 1.1rem; margin-top: 1.5rem; }}

        p, li {{ margin-bottom: 1rem; }}
        
        a {{
            color: var(--text);
            text-decoration: none;
            border-bottom: 1px solid var(--accent);
            transition: color 0.2s, border-color 0.2s;
        }}

        a:hover {{
            color: var(--accent);
            border-bottom-color: transparent;
        }}

        ul {{
            padding-left: 1.5rem;
            list-style-type: square;
        }}

        .muted {{ color: var(--muted); font-size: 0.9em; }}
        .small {{ font-size: 0.85rem; }}

        /* Section header (flex row with right-aligned metadata) */
        .section-header {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 1rem;
        }}

        /* Header */
        .header-row {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 1rem;
        }}

        .header-icons {{
            display: flex;
            gap: 0.75rem;
            align-items: center;
        }}

        .header-icon {{
            color: var(--muted);
            border: none;
            transition: color 0.2s;
            display: flex;
        }}

        .header-icon:hover {{
            color: var(--accent);
        }}

        /* Navigation */
        nav {{
            margin: 1.5rem 0 3rem 0;
            padding: 1rem 0;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        nav a {{ border-bottom: none; }}
        nav a:hover {{ color: var(--accent); }}
        .nav-separator {{ color: var(--muted); padding: 0 0.5rem; }}

        /* Sections */
        section {{
            margin-bottom: 4rem;
            padding-left: 1rem;
            border-left: 3px solid transparent;
            transition: border-color 0.3s;
        }}

        section:hover {{
            border-left-color: var(--selection);
        }}

        /* Content Grid (Books & Albums) */
        .book-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
            gap: 1rem 2rem;
        }}

        .book-group {{
            margin-bottom: 0.5rem;
            padding-left: 1rem;
            border-left: 2px solid var(--border);
            transition: border-color 0.2s;
        }}

        .book-group:hover {{
            border-left-color: var(--accent);
        }}

        .book-year {{
            font-weight: bold;
            display: block;
            margin-bottom: 0.3rem;
        }}

        .book-title {{
            display: block;
            color: var(--muted);
            font-size: 0.9em;
            line-height: 1.5;
        }}

        .sparkline {{
            color: var(--muted);
            font-size: 0.85rem;
            margin-bottom: 1rem;
            line-height: 1.6;
        }}

        .album-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
            gap: 1rem 2rem;
        }}

        .album-group {{
            margin-bottom: 0.5rem;
            padding-left: 1rem;
            border-left: 2px solid var(--border);
            transition: border-color 0.2s;
        }}

        .album-group:hover {{
            border-left-color: var(--accent);
        }}

        .album-year {{
            font-weight: bold;
            display: block;
            margin-bottom: 0.3rem;
        }}

        .album-title {{
            display: block;
            font-weight: bold;
            border-bottom: none;
        }}

        .album-title:hover {{
            color: var(--accent);
        }}

        .album-note {{
            display: block;
            color: var(--muted);
            font-size: 0.85em;
            font-style: italic;
            line-height: 1.4;
            margin-bottom: 0.5rem;
        }}

        /* Theme Toggle */
        .theme-toggle {{
            position: fixed;
            top: 1.5rem;
            right: 1.5rem;
            background: none;
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.5rem;
            cursor: pointer;
            border-radius: 4px;
            font-family: inherit;
            line-height: 1;
            z-index: 100;
        }}
        
        .theme-toggle:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}

        .back-to-top {{
            display: block;
            text-align: right;
            font-size: 0.8rem;
            margin-top: 1rem;
            color: var(--muted);
            border: none;
        }}
        .back-to-top:hover {{ color: var(--accent); }}

        /* Responsive */
        @media (max-width: 768px) {{
            body {{ padding: 1rem; }}
            h1 {{ font-size: 1.7rem; }}
            nav {{ font-size: 0.9rem; }}
            .theme-toggle {{ top: 1rem; right: 1rem; }}
            .book-grid, .album-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">☀</button>

    <div class="container">
        
        <header>
            <div class="header-row">
                <h1>Kyle Fring</h1>
                <div class="header-icons">
                    {header_icons}
                </div>
            </div>
            <nav>
                <a href="#now">Now</a> <span class="nav-separator">·</span>
                <a href="#bookshelf">Bookshelf</a> <span class="nav-separator">·</span>
                <a href="#albums">Albums</a> <span class="nav-separator">·</span>
                <a href="#epilogue">Epilogue</a>
            </nav>
        </header>

        <main>
            <section id="now">
                <div class="section-header">
                    <h2>Now</h2>
                    <span class="muted small">{now_content_date}</span>
                </div>
                
{now_html}

                <a href="#top" class="back-to-top">↑</a>
            </section>

            <section id="bookshelf">
                <h2>Bookshelf</h2>
                
{books_html}
                <a href="#top" class="back-to-top">↑</a>
            </section>

            <section id="albums">
                <h2>Albums</h2>
                
{albums_html}
                <a href="#top" class="back-to-top">↑</a>
            </section>

            <section id="epilogue">
                <h2>Epilogue</h2>
                <p>Previous iterations: <a href="http://v3.fring.io">v3</a> · <a href="http://v2.fring.io">v2</a> · <a href="http://v1.kfring.com">v1</a></p>
                <p class="muted small">Credit to <a href="http://bettermotherfuckingwebsite.com/">bettermotherfuckingwebsite.com</a></p>
                <p class="muted small">Built {build_date}</p>
                <a href="#top" class="back-to-top">↑</a>
            </section>

        </main>
    </div>

    <script>
        const toggleBtn = document.getElementById('theme-toggle');
        const html = document.documentElement;
        
        // Check local storage or system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {{
            html.setAttribute('data-theme', savedTheme);
            updateIcon(savedTheme);
        }} else if (window.matchMedia('(prefers-color-scheme: light)').matches) {{
            html.setAttribute('data-theme', 'light');
            updateIcon('light');
        }}

        function updateIcon(theme) {{
            toggleBtn.textContent = theme === 'light' ? '☾' : '☀';
        }}

        toggleBtn.addEventListener('click', () => {{
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        }});
    </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Regenerate v4 HTML from content JSON")
    parser.add_argument(
        "--preview", action="store_true", help="Print HTML to stdout instead of writing"
    )
    args = parser.parse_args()

    content_dir = Path("content")
    output_file = Path("sites/v4/index.html")

    print("Regenerating v4 HTML")
    print("=" * 50)

    books_data = load_json(content_dir / "books.json")
    albums_data = load_json(content_dir / "albums.json")
    now_data = load_json(content_dir / "now.json")

    print(f"  Books:  {len(books_data['books'])}")
    print(f"  Albums: {len(albums_data['albums'])}")

    full_html = generate_full_html(books_data, albums_data, now_data)

    if args.preview:
        print("\n" + full_html)
    else:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(full_html)

        size_kb = len(full_html.encode("utf-8")) / 1024
        print(f"\n✓ Generated {output_file} ({size_kb:.1f} KB)")
        print(f"  Sections: Now, Bookshelf, Albums, Epilogue")


if __name__ == "__main__":
    main()
