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
  - Elsewhere section (from now.json links)
  - Epilogue (static)

Usage:
    python infrastructure/regenerate_v4_html.py
    python infrastructure/regenerate_v4_html.py --preview
"""

import json
import html
import argparse
from pathlib import Path
from collections import OrderedDict


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def group_books_by_year(books: list) -> OrderedDict:
    """Group books by year, maintaining order (newest first). yearLabel books go last."""
    groups = OrderedDict()
    for book in books:
        key = book.get("yearLabel") or str(book.get("year", "Unknown"))
        if key not in groups:
            groups[key] = []
        groups[key].append(book["title"])
    return groups


def build_album_sparkline(albums: list) -> str:
    """Build a month-by-month sparkline for album listening activity."""
    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    blocks = " ▁▂▃▄▅▆█"
    counts = [0] * 12
    for album in albums:
        date_str = album.get("listenedDate", "")
        if date_str and len(date_str) >= 7:
            month = int(date_str[5:7]) - 1
            counts[month] += 1

    max_count = max(counts) if max(counts) > 0 else 1
    parts = []
    for i, count in enumerate(counts):
        if count == 0:
            parts.append(f"{month_names[i]} {blocks[0]}")
        else:
            level = max(1, round(count / max_count * (len(blocks) - 1)))
            parts.append(f"{month_names[i]} {blocks[level]}")
    return "  ".join(parts)


def generate_book_groups_html(books: list, indent: str = "                ") -> str:
    """Generate book-grid HTML from books list."""
    groups = group_books_by_year(books)
    total = len(books)
    years = [k for k in groups if k != "<2015"]
    year_range = f"{min(years)}–{max(years)}" if years else ""
    if "<2015" in groups:
        year_range += " + prior"

    lines = []
    lines.append(
        f'{indent}<p class="muted small">{total} books tracked · {year_range}</p>'
    )
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


def generate_albums_html(albums: list, indent: str = "                ") -> str:
    """Generate flat album list HTML, sorted by listened date (newest first)."""
    sorted_albums = sorted(
        albums, key=lambda a: a.get("listenedDate", ""), reverse=True
    )
    total = len(sorted_albums)

    listened_years = {
        a["listenedDate"][:4] for a in sorted_albums if a.get("listenedDate")
    }
    release_years = [
        a.get("releaseYear") for a in sorted_albums if a.get("releaseYear")
    ]
    year_span = f"{min(release_years)}–{max(release_years)}" if release_years else ""
    listened_label = ", ".join(sorted(listened_years, reverse=True))

    sparkline = build_album_sparkline(sorted_albums)

    lines = []
    lines.append(
        f'{indent}<p class="muted small">{total} albums · listened {listened_label} · releases spanning {year_span}</p>'
    )
    lines.append(f'{indent}<div class="sparkline" aria-hidden="true">')
    lines.append(f"{indent}    {sparkline}")
    lines.append(f"{indent}</div>")

    for album in sorted_albums:
        artist = html.escape(album["artist"])
        name = html.escape(album["album"])
        release_year = album.get("releaseYear", "")
        title_text = f"{artist} — {name}"
        if release_year:
            title_text += f" ({release_year})"

        lines.append(f'{indent}<div class="album-entry">')

        spotify_url = album.get("spotifyUrl")
        if spotify_url:
            lines.append(
                f'{indent}    <a href="{html.escape(spotify_url)}" target="_blank" class="album-title">{title_text}</a>'
            )
        else:
            lines.append(f'{indent}    <span class="album-title">{title_text}</span>')

        if album.get("notes"):
            lines.append(
                f'{indent}    <span class="album-note">{html.escape(album["notes"])}</span>'
            )

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


def generate_elsewhere_html(now: dict, indent: str = "                ") -> str:
    """Generate Elsewhere section from now.json links."""
    links = now["links"]
    parts = []
    if "github" in links:
        parts.append(f'<a href="https://github.com/{links["github"]}/">github</a>')
    if "linkedin" in links:
        parts.append(
            f'<a href="https://linkedin.com/in/{links["linkedin"]}/">linkedin</a>'
        )
    if "goodreads" in links:
        parts.append(
            f'<a href="https://goodreads.com/{links["goodreads"]}/">goodreads</a>'
        )

    separator = ' <span class="nav-separator">·</span>\n' + indent + "    "
    return f"{indent}<p>\n{indent}    {separator.join(parts)}\n{indent}</p>"


def generate_full_html(books_data: dict, albums_data: dict, now_data: dict) -> str:
    """Generate the complete v4 HTML page."""
    books_html = generate_book_groups_html(books_data["books"])
    albums_html = generate_albums_html(albums_data["albums"])
    now_html = generate_now_html(now_data)
    elsewhere_html = generate_elsewhere_html(now_data)

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

        .album-entry {{
            margin-bottom: 1.5rem;
            padding-left: 1rem;
            border-left: 2px solid var(--border);
            transition: border-color 0.2s;
        }}

        .album-entry:hover {{
            border-left-color: var(--accent);
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
            margin-top: 0.2rem;
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
            .book-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">☀</button>

    <div class="container">
        
        <header>
            <h1>Kyle Fring</h1>
            <nav>
                <a href="#now">Now</a> <span class="nav-separator">·</span>
                <a href="#bookshelf">Bookshelf</a> <span class="nav-separator">·</span>
                <a href="#albums">Albums</a> <span class="nav-separator">·</span>
                <a href="#elsewhere">Elsewhere</a> <span class="nav-separator">·</span>
                <a href="#epilogue">Epilogue</a>
            </nav>
        </header>

        <main>
            <section id="now">
                <h2>Now</h2>
                
{now_html}

                <p class="muted small">Last updated: February 2026</p>
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

            <section id="elsewhere">
                <h2>Elsewhere</h2>
{elsewhere_html}
                <a href="#top" class="back-to-top">↑</a>
            </section>

            <section id="epilogue">
                <h2>Epilogue</h2>
                <p>Previous iterations: <a href="http://v3.fring.io">v3</a> · <a href="http://v2.fring.io">v2</a> · <a href="http://v1.kfring.com">v1</a></p>
                <p class="muted small">Credit to <a href="http://bettermotherfuckingwebsite.com/">bettermotherfuckingwebsite.com</a></p>
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
        print(f"  Sections: Now, Bookshelf, Albums, Elsewhere, Epilogue")


if __name__ == "__main__":
    main()
