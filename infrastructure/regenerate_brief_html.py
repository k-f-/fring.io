#!/usr/bin/env python3
"""
regenerate_brief_html.py - Regenerate sites/v4/brief/ from content/brief/*.md.

This is the fring.io-native renderer for the AI Weekly Brief. It replaces the
render_site() step that used to run on the Mac mini as part of
scripts/mac-mini/brief-compiler.py — that script drove the weekly compile
(Miniflux fetch, headless Claude calls, IMAP intake) and pushed its own
render straight to a dedicated fring.io clone + NAS mirror. This script only
does the render: it reads the weekly markdown that already lives under
content/brief/ in this repo and turns it into the HTML tree under
sites/v4/brief/, the same way infrastructure/regenerate_v4_html.py turns
content/*.json into sites/v4/index.html. GitHub Actions (deploy.yml) then
syncs sites/v4 to S3 on every push to main.

Reads from:
  - content/brief/????-??-??.md  (one file per week, e.g. 2026-08-18.md)
  - content/brief/about.md
  - content/brief/sources.md

Generates:
  - sites/v4/brief/<date>.html   for every week
  - sites/v4/brief/index.html    latest week, duplicated
  - sites/v4/brief/about.html
  - sites/v4/brief/latest.json

Usage:
    python infrastructure/regenerate_brief_html.py
    python infrastructure/regenerate_brief_html.py --preview
"""

import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

CONTENT_DIR = Path("content/brief")
OUTPUT_DIR = Path("sites/v4/brief")
SITE_URL = "https://fring.io/brief"


# ── HTML rendering ──────────────────────────────────────────────────────────
# Blog-shaped, styled to match fring.io v4 (infrastructure/regenerate_v4_html.py
# in the k-f-/fring.io repo): mono font stack, dark default + light toggle, teal
# accent, underline-accent links. Every page is re-rendered each run so the
# archive sidebar stays current on old posts. All links are relative so the same
# tree works at the NAS root (brief.fring.io) and under fring.io/brief/.

PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="AI Weekly Brief — vendor, Databricks, and regulatory AI news, compiled weekly.">
<style>
:root {{
    --bg: #1a1a1a; --text: #e0e0e0; --muted: #888; --accent: #88dcb4;
    --border: #333; --code-bg: #222; --selection: rgba(94, 234, 212, 0.2);
    --font-stack: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
}}
[data-theme="light"] {{
    --bg: #fafafa; --text: #1a1a1a; --muted: #666; --accent: #278061;
    --border: #ddd; --code-bg: #f0f0f0; --selection: rgba(13, 148, 136, 0.2);
}}
* {{ box-sizing: border-box; }}
::selection {{ background: var(--accent); color: var(--bg); }}
body {{
    background-color: var(--bg); color: var(--text); font-family: var(--font-stack);
    font-size: 16px; line-height: 1.6; margin: 0; padding: 2rem;
    transition: background-color 0.3s ease, color 0.3s ease;
}}
.container {{ max-width: 1100px; margin: 0 auto; }}
h1, h2, h3 {{ font-weight: 700; margin-top: 2.5rem; margin-bottom: 1rem;
    line-height: 1.2; letter-spacing: -0.03em; }}
h1 {{ font-size: 2rem; margin-top: 0; }}
h2 {{ font-size: 1.4rem; color: var(--accent); }}
h3 {{ font-size: 1.1rem; margin-top: 1.5rem; }}
p, li {{ margin-bottom: 0.6rem; }}
a {{ color: var(--text); text-decoration: underline;
    text-decoration-color: var(--accent); text-decoration-thickness: 1px;
    text-underline-offset: 4px; transition: color 0.2s, text-decoration-color 0.2s; }}
a:hover {{ color: var(--accent); text-decoration-color: transparent; }}
ul {{ padding-left: 1.5rem; list-style-type: square; }}
.muted {{ color: var(--muted); font-size: 0.9em; }}
.small {{ font-size: 0.85rem; }}
.header-row {{ display: flex; align-items: baseline;
    justify-content: space-between; gap: 1rem; }}
nav {{ margin: 1.5rem 0 2.5rem 0; padding: 1rem 0; border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border); display: flex; flex-wrap: wrap; gap: 0.5rem; }}
nav a {{ text-decoration: none; }}
nav a:hover {{ color: var(--accent); }}
.nav-separator {{ color: var(--muted); padding: 0 0.5rem; }}
.layout {{ display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 3rem; }}
@media (max-width: 800px) {{
  .layout {{ grid-template-columns: 1fr; }}
  .sidebar {{ position: static; order: 2; }}
  article {{ order: 1; }}
}}
article {{ max-width: 80ch; min-width: 0; }}
article h2 {{ border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }}
.sidebar {{ position: sticky; top: 1rem; align-self: start;
    max-height: calc(100vh - 2rem); overflow-y: auto; font-size: 0.85rem; }}
.sidebar h2 {{ font-size: 1rem; margin-top: 1.5rem; }}
.sidebar h2:first-child {{ margin-top: 0; }}
.sidebar ul {{ list-style: none; padding: 0; }}
.sidebar ul ul {{ padding-left: 1rem; list-style: none; }}
.sidebar li {{ margin-bottom: 0.4rem; }}
#theme-toggle {{ background: none; border: 1px solid var(--border); color: var(--muted);
    font-family: var(--font-stack); cursor: pointer; padding: 0.2rem 0.6rem;
    border-radius: 4px; }}
#theme-toggle:hover {{ color: var(--accent); border-color: var(--accent); }}
footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border);
    color: var(--muted); font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="container">
    <header>
        <div class="header-row">
            <h1>AI Weekly Brief</h1>
            <button id="theme-toggle" aria-label="Toggle theme">&#9788;</button>
        </div>
        <nav>
            <a href="https://fring.io">fring.io</a> <span class="nav-separator">&middot;</span>
            <a href="./">Latest</a> <span class="nav-separator">&middot;</span>
            <a href="about.html">About this Page</a>{posted_block}
        </nav>
    </header>
    <div class="layout">
        <aside class="sidebar">
{toc}
            <h2>Archive</h2>
            <ul>
{archive}
            </ul>
        </aside>
        <article>
{body}
        </article>
    </div>
    <footer>Compiled {stamp} &middot; sources linked inline &middot; <a href="https://fring.io">fring.io</a></footer>
</div>
<script>
const toggleBtn = document.getElementById('theme-toggle');
const html = document.documentElement;
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {{ html.setAttribute('data-theme', savedTheme); updateIcon(savedTheme); }}
else if (window.matchMedia('(prefers-color-scheme: light)').matches) {{
    html.setAttribute('data-theme', 'light'); updateIcon('light'); }}
function updateIcon(theme) {{ toggleBtn.textContent = theme === 'light' ? '\\u263e' : '\\u2600'; }}
toggleBtn.addEventListener('click', () => {{
    const newTheme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme); updateIcon(newTheme);
}});
</script>
</body>
</html>
"""


def md_to_html(text):
    """Returns (body_html, toc_html). The toc extension stamps ids on headings;
    the sidebar TOC is built from its token tree (h2 sections, h3 nested)."""
    try:
        import markdown
    except ImportError:
        print("WARNING: python 'markdown' package missing — shipping <pre> fallback",
              file=sys.stderr)
        return "<pre>" + html.escape(text) + "</pre>", ""
    md = markdown.Markdown(extensions=["extra", "toc"])
    # python-markdown ignores a list that directly follows a paragraph line;
    # insert the missing blank line so model output renders as a real list.
    text = re.sub(r"(?m)^(?![ \t]*(?:[-*]|\d+\.)[ \t])(.+)\n(?=(?:[-*]|\d+\.)[ \t])", "\\1\n\n", text)
    body = md.convert(text)

    def items(tokens):
        out = []
        for t in tokens:
            # toc_tokens names arrive already HTML-escaped ("Data &amp; Platform");
            # unescape first so we escape exactly once.
            name = html.escape(html.unescape(t["name"]))
            out.append(f'<li><a href="#{t["id"]}">{name}</a>')
            if t.get("children"):
                out.append("<ul>" + "".join(items(t["children"])) + "</ul>")
            out.append("</li>")
        return out

    # Skip the single h1 title level; the TOC starts at the h2 sections.
    tokens = md.toc_tokens
    if len(tokens) == 1 and tokens[0].get("children"):
        tokens = tokens[0]["children"]
    toc = ""
    if tokens:
        toc = ('            <h2>Contents</h2>\n            <ul class="toc">'
               + "".join(items(tokens)) + "</ul>")
    return body, toc


def pretty_date(iso_date):
    return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%B %d, %Y")


# ── Orchestration ────────────────────────────────────────────────────────────

def discover_weeks():
    """Dated post filenames under content/brief/, newest first. Same glob shape
    brief-compiler.py's sync_briefs_from_repo used against this directory — it
    structurally excludes about.md and sources.md (they don't match ????-??-??)."""
    return sorted((p.stem for p in CONTENT_DIR.glob("????-??-??.md")), reverse=True)


def archive_html(weeks, current):
    """Sidebar archive list: the current week is a muted (non-link) span,
    every other week links to its own <date>.html."""
    items = []
    for w in weeks:
        label = pretty_date(w)
        if w == current:
            items.append(f'                <li><span class="muted">{label}</span></li>')
        else:
            items.append(f'                <li><a href="{w}.html">{label}</a></li>')
    return "\n".join(items)


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate sites/v4/brief/ from content/brief/*.md")
    parser.add_argument(
        "--preview", action="store_true",
        help="Print the index (latest week) HTML to stdout instead of writing")
    args = parser.parse_args()

    print("Regenerating brief HTML")
    print("=" * 50)

    weeks = discover_weeks()
    if not weeks:
        # deploy.yml syncs sites/v4 to S3 with --delete, so writing an empty
        # tree here would take down the live /brief section. Bail loudly
        # instead of silently producing nothing.
        print(f"ERROR: no dated posts found under {CONTENT_DIR}/ "
              "(expected files like 2026-08-18.md) — refusing to write an "
              "empty tree", file=sys.stderr)
        return 1

    print(f"  Weeks: {len(weeks)} ({weeks[-1]} .. {weeks[0]})")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    pages = {}  # filename -> html, built in memory first so --preview works
    for w in weeks:
        body, toc = md_to_html((CONTENT_DIR / f"{w}.md").read_text())
        page = PAGE.format(
            title=f"AI Weekly Brief — {pretty_date(w)}",
            posted_block=f' <span class="nav-separator">&middot;</span> <span class="muted">Posted {pretty_date(w)}</span>',
            body=body, toc=toc, archive=archive_html(weeks, w), stamp=stamp)
        pages[f"{w}.html"] = page
    pages["index.html"] = pages[f"{weeks[0]}.html"]

    about_src = CONTENT_DIR / "about.md"
    if about_src.exists():
        about_body, _ = md_to_html(about_src.read_text())
        sources_src = CONTENT_DIR / "sources.md"
        sources_block = ""
        if sources_src.exists():
            sources_html, _ = md_to_html(sources_src.read_text())
            sources_block = "            <h2>Sources</h2>\n" + sources_html
        pages["about.html"] = PAGE.format(
            title="AI Weekly Brief — About this Page",
            posted_block="",
            body=about_body, toc=sources_block,
            archive=archive_html(weeks, None), stamp=stamp)

    # No "counts" key here (unlike the old STATE/weeks/*/meta.json-derived
    # version): those came from the Miniflux fetch counts, which only exist
    # on the Mac mini's compile run. GitHub Actions has no Miniflux access,
    # and the only consumer of latest.json (the fring.io homepage "latest
    # brief" pointer) only reads date/url — so counts is simply dropped.
    latest_json = json.dumps({
        "date": weeks[0],
        "url": f"{SITE_URL}/{weeks[0]}.html",
    }, indent=2)

    if args.preview:
        print("\n" + pages["index.html"])
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in pages.items():
        (OUTPUT_DIR / name).write_text(content)
    (OUTPUT_DIR / "latest.json").write_text(latest_json)

    print(f"\n  Wrote {len(pages) + 1} file(s) to {OUTPUT_DIR}/")
    print(f"  Latest: {weeks[0]} -> {SITE_URL}/{weeks[0]}.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
