#!/usr/bin/env python3
"""
Parse now.md and regenerate now.json
Supports round-trip conversion: JSON → MD → JSON (lossless)

Usage:
    # Parse and update now.json
    ./parse_now.py

    # Preview without writing
    ./parse_now.py --preview
"""

import re
import json
from datetime import datetime
from pathlib import Path
import argparse


class NowMarkdownParser:
    """Parse now.md back to JSON structure"""

    def __init__(self, content_dir: Path = Path("content")):
        self.content_dir = content_dir

    def parse_now(self, input_file: Path = None) -> dict:
        """Parse now.md to JSON structure"""
        if input_file is None:
            input_file = self.content_dir / "now.md"

        with open(input_file) as f:
            content = f.read()

        # Extract JSON metadata and location from HTML comment
        meta_match = re.search(r"<!--\n(.+?)\n-->", content, re.DOTALL)
        if meta_match:
            meta_json = json.loads(meta_match.group(1))
            meta = meta_json.get("meta", {})
            location = meta_json.get("location", {})
        else:
            meta = {
                "version": "1.0",
                "description": "Current activities and status - /now page content",
            }
            location = {}

        meta["lastUpdated"] = datetime.now().isoformat()
        if "contentUpdated" not in meta:
            meta["contentUpdated"] = datetime.now().strftime("%Y-%m-%d")

        sections = {}

        # Parse Life section
        life_match = re.search(r"## Life\n\n(.+?)(?=\n\n##|\Z)", content, re.DOTALL)
        if life_match:
            life_text = life_match.group(1).strip()

            # Extract inline markdown links as highlights
            highlights = []
            link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
            for match in re.finditer(link_pattern, life_text):
                highlights.append({"text": match.group(1), "url": match.group(2)})

            sections["life"] = {"text": life_text, "highlights": highlights}

        # Parse Work section
        work_match = re.search(r"## Work\n\n(.+?)(?=\n\n##|\Z)", content, re.DOTALL)
        if work_match:
            work_content = work_match.group(1).strip()
            work_data = {}

            # Current Role
            role_match = re.search(r"\*\*Current Role:\*\* (.+)", work_content)
            if role_match:
                work_data["currentRole"] = role_match.group(1).strip()

            # Company
            company_match = re.search(r"\*\*Company:\*\* (.+)", work_content)
            if company_match:
                work_data["company"] = company_match.group(1).strip()

            # Description (text between Company and Previous Role)
            desc_match = re.search(
                r"\*\*Company:\*\* .+?\n\n(.+?)(?=\n\*\*Previous Role|\Z)",
                work_content,
                re.DOTALL,
            )
            if desc_match:
                work_data["description"] = desc_match.group(1).strip()

            # Previous Role
            prev_role_match = re.search(
                r"\*\*Previous Role:\*\* (.+?)(?:\s\s|\n)", work_content
            )
            if prev_role_match:
                prev_title = prev_role_match.group(1).strip()
                # Get description after Previous Role
                prev_desc_match = re.search(
                    r"\*\*Previous Role:\*\* .+?\n(.+?)(?=\n\n##|\Z)",
                    work_content,
                    re.DOTALL,
                )
                prev_desc = prev_desc_match.group(1).strip() if prev_desc_match else ""

                work_data["previousRole"] = {
                    "title": prev_title,
                    "description": prev_desc,
                }

            sections["work"] = work_data

        # Parse Future section
        future_match = re.search(
            r"## Future\n\n.+?\n\n(.+?)(?=\n\n---|\n\n##|\Z)", content, re.DOTALL
        )
        if future_match:
            future_content = future_match.group(1).strip()
            # Extract desires from bullet list
            desires = re.findall(r"^- (.+)$", future_content, re.MULTILINE)
            sections["future"] = {"desires": desires}

        # Parse Elsewhere/links section
        elsewhere_match = re.search(
            r"## Elsewhere\n\n(.+?)(?=\n\n---|\Z)", content, re.DOTALL
        )
        links = {}
        if elsewhere_match:
            elsewhere_content = elsewhere_match.group(1).strip()

            # GitHub
            github_match = re.search(
                r"\*\*GitHub:\*\* \[(.+?)\]\(https://github.com/(.+?)\)",
                elsewhere_content,
            )
            if github_match:
                links["github"] = github_match.group(2)

            # LinkedIn
            linkedin_match = re.search(
                r"\*\*LinkedIn:\*\* \[(.+?)\]\(https://linkedin.com/in/(.+?)\)",
                elsewhere_content,
            )
            if linkedin_match:
                links["linkedin"] = linkedin_match.group(2)

            # Goodreads
            goodreads_match = re.search(
                r"\*\*Goodreads:\*\* \[(.+?)\]\(https://goodreads.com/(.+?)\)",
                elsewhere_content,
            )
            if goodreads_match:
                links["goodreads"] = goodreads_match.group(2)

        return {
            "meta": meta,
            "location": location,
            "sections": sections,
            "links": links,
        }

    def save_now_json(self, data: dict, output_file: Path = None):
        """Save parsed data to now.json"""
        if output_file is None:
            output_file = self.content_dir / "now.json"

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✓ Parsed /now page from markdown")
        print(f"  Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse now.md to JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input markdown file (default: content/now.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file (default: content/now.json)",
    )
    parser.add_argument(
        "--preview", action="store_true", help="Preview output without writing files"
    )

    args = parser.parse_args()

    md_parser = NowMarkdownParser()

    print("Now Page Markdown Parser")
    print("=" * 50)
    print("")

    data = md_parser.parse_now(args.input)

    if args.preview:
        print("Preview mode - would create now.json with:")
        print("")
        print(json.dumps(data, indent=2))
    else:
        md_parser.save_now_json(data, args.output)
        print("")
        print(
            f"Location: {data['location'].get('city', 'N/A')}, {data['location'].get('state', 'N/A')}"
        )
        print(f"Sections: {', '.join(data['sections'].keys())}")
        print(f"Links: {', '.join(data['links'].keys())}")
