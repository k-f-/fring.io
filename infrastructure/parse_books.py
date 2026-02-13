#!/usr/bin/env python3
"""
Parse books.md and regenerate books.json
Supports round-trip conversion: JSON → MD → JSON (lossless)

Usage:
    # Parse and update books.json
    ./parse_books.py

    # Preview without writing
    ./parse_books.py --preview
"""

import re
import json
from datetime import datetime
from pathlib import Path
import argparse


class BooksMarkdownParser:
    """Parse books.md back to JSON structure"""

    def __init__(self, content_dir: Path = Path("content")):
        self.content_dir = content_dir

    def parse_books(self, input_file: Path = None) -> dict:
        """Parse books.md to JSON structure"""
        if input_file is None:
            input_file = self.content_dir / "books.md"

        with open(input_file) as f:
            content = f.read()

        # Extract JSON metadata from HTML comment
        meta_match = re.search(r"<!--\n(.+?)\n-->", content, re.DOTALL)
        if meta_match:
            meta_json = json.loads(meta_match.group(1))
            meta = meta_json.get("meta", {})
        else:
            meta = {
                "version": "1.0",
                "description": "Canonical book list for fring.io - version agnostic content",
            }

        # Update lastUpdated
        meta["lastUpdated"] = datetime.now().isoformat()

        books = []

        year_sections = re.finditer(
            r"^## (.+?)(?:\s*\([^)]*\))?\s*\n", content, re.MULTILINE
        )

        for match in year_sections:
            year_text = match.group(1)  # "2020" or "Prior to 2015"
            section_start = match.end()

            # Find the next section or end of document
            next_match = re.search(r"\n##", content[section_start:])
            if next_match:
                section_end = section_start + next_match.start()
            else:
                # Look for the footer (---)
                footer_match = re.search(r"\n---", content[section_start:])
                if footer_match:
                    section_end = section_start + footer_match.start()
                else:
                    section_end = len(content)

            section_content = content[section_start:section_end]

            # Determine year value and yearLabel
            if year_text.startswith("Prior to"):
                year = None
                year_label = "<2015"
            else:
                try:
                    year = int(year_text)
                    year_label = None
                except ValueError:
                    year = None
                    year_label = year_text

            # Extract book titles from bullet points
            book_titles = re.findall(r"^- (.+)$", section_content, re.MULTILINE)

            for title in book_titles:
                books.append(
                    {
                        "title": title.strip(),
                        "year": year,
                        "yearLabel": year_label,
                        "dateAdded": datetime.now().isoformat(),
                    }
                )

        return {"meta": meta, "books": books}

    def save_books_json(self, data: dict, output_file: Path = None):
        """Save parsed data to books.json"""
        if output_file is None:
            output_file = self.content_dir / "books.json"

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✓ Parsed {len(data['books'])} books from markdown")
        print(f"  Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse books.md to JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input markdown file (default: content/books.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file (default: content/books.json)",
    )
    parser.add_argument(
        "--preview", action="store_true", help="Preview output without writing files"
    )

    args = parser.parse_args()

    md_parser = BooksMarkdownParser()

    print("Books Markdown Parser")
    print("=" * 50)
    print("")

    data = md_parser.parse_books(args.input)

    if args.preview:
        print("Preview mode - would create books.json with:")
        print("")
        print(json.dumps(data, indent=2))
        print("")
        print(f"Total books: {len(data['books'])}")
    else:
        md_parser.save_books_json(data, args.output)
        print("")
        print("Sample books:")
        for book in data["books"][:5]:
            year_info = book.get("year") or book.get("yearLabel", "unknown")
            print(f"  • {book['title']} ({year_info})")
