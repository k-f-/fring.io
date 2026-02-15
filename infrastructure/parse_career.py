#!/usr/bin/env python3
"""
Parse career.md and regenerate career.json
Supports round-trip conversion: JSON → MD → JSON (lossless)

Usage:
    # Parse and update career.json
    ./parse_career.py

    # Preview without writing
    ./parse_career.py --preview
"""

import re
import json
from datetime import datetime
from pathlib import Path
import argparse


class CareerMarkdownParser:
    """Parse career.md back to JSON structure"""

    def __init__(self, content_dir: Path = Path("content")):
        self.content_dir = content_dir

    def _format_date(self, date_str: str) -> str:
        """Convert 'Month YYYY' to 'YYYY-MM' format"""
        try:
            dt = datetime.strptime(date_str, "%B %Y")
            return dt.strftime("%Y-%m")
        except:
            return date_str

    def parse_career(self, input_file: Path = None) -> dict:
        """Parse career.md to JSON structure"""
        if input_file is None:
            input_file = self.content_dir / "career.md"

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
                "description": "Professional experience and career history",
            }

        meta["lastUpdated"] = datetime.now().isoformat()
        if "contentUpdated" not in meta:
            meta["contentUpdated"] = datetime.now().strftime("%Y-%m-%d")

        # Parse Summary section
        summary = {}

        # Headline and Years
        headline_match = re.search(r"\*\*Headline:\*\* (.+)", content)
        if headline_match:
            summary["headline"] = headline_match.group(1).strip()

        years_match = re.search(r"\*\*Years of Experience:\*\* (.+)", content)
        if years_match:
            summary["yearsOfExperience"] = years_match.group(1).strip()

        # Specialties
        specialties_match = re.search(
            r"### Specialties\n(.+?)(?=\n###|\n\*\*)", content, re.DOTALL
        )
        if specialties_match:
            specialties = re.findall(
                r"^- (.+)$", specialties_match.group(1), re.MULTILINE
            )
            summary["specialties"] = specialties

        # Current Stack (nested structure)
        stack_match = re.search(
            r"### Current Stack\n\n(.+?)(?=\n\*\*Background)", content, re.DOTALL
        )
        if stack_match:
            stack_content = stack_match.group(1)
            current_stack = {}

            # Find all categories (Code, Cloud, Visualization, etc.)
            category_matches = re.finditer(
                r"\*\*([^:]+):\*\*\n((?:- .+\n)+)", stack_content
            )
            for cat_match in category_matches:
                category_name = cat_match.group(1).strip().lower()
                # Convert to camelCase
                if " " in category_name:
                    parts = category_name.split()
                    category_name = parts[0] + "".join(
                        p.capitalize() for p in parts[1:]
                    )

                items = re.findall(r"^- (.+)$", cat_match.group(2), re.MULTILINE)
                current_stack[category_name] = items

            summary["currentStack"] = current_stack

        # Background
        background_match = re.search(r"\*\*Background:\*\* (.+)", content)
        if background_match:
            summary["background"] = background_match.group(1).strip()

        # Parse Experience entries
        experience = []

        # Find all experience sections (between ### and ---)
        exp_section_match = re.search(
            r"## Experience\n\n(.+?)(?=\n## Preferences|\Z)", content, re.DOTALL
        )
        if exp_section_match:
            exp_content = exp_section_match.group(1)

            # Split by --- separators
            exp_entries = re.split(r"\n---\n", exp_content)

            for entry in exp_entries:
                if not entry.strip():
                    continue

                exp_data = {}

                # Title
                title_match = re.search(r"^### (.+)$", entry, re.MULTILINE)
                if title_match:
                    exp_data["title"] = title_match.group(1).strip()

                # Company (with optional type in parentheses)
                company_match = re.search(r"\*\*(.+?)\*\*\s*$", entry, re.MULTILINE)
                if company_match:
                    company_line = company_match.group(1).strip()
                    # Check for type in parentheses
                    type_match = re.search(r"(.+?)\s+\((.+?)\)$", company_line)
                    if type_match:
                        exp_data["company"] = type_match.group(1).strip()
                        exp_data["companyType"] = type_match.group(2).strip()
                    else:
                        exp_data["company"] = company_line

                # Location
                location_match = re.search(r"\*\*Location:\*\* (.+)", entry)
                if location_match:
                    exp_data["location"] = location_match.group(1).strip()

                # Period (start and end dates + duration)
                period_match = re.search(
                    r"\*\*Period:\*\* (.+?)(?: - (.+?))?(?:\s+\((.+?)\))?(?:\s\s|\n)",
                    entry,
                    re.DOTALL,
                )
                if period_match:
                    start_date_str = period_match.group(1).strip()
                    end_date_str = (
                        period_match.group(2).strip() if period_match.group(2) else None
                    )
                    duration = (
                        period_match.group(3).strip() if period_match.group(3) else None
                    )

                    # Convert dates to YYYY-MM format
                    exp_data["startDate"] = self._format_date(start_date_str)

                    if end_date_str and end_date_str != "Present":
                        exp_data["endDate"] = self._format_date(end_date_str)
                    else:
                        exp_data["endDate"] = None

                    if duration:
                        exp_data["duration"] = duration

                # Current Role
                if re.search(r"\*\*Current Role:\*\* ✓", entry):
                    exp_data["current"] = True

                # Description (text between Current Role/Period and Highlights or Skills)
                desc_match = re.search(
                    r"(?:Current Role: ✓\n\n|Period:.*?\n\n)(.+?)(?=\n\*\*Highlights|\n\*\*Skills|\Z)",
                    entry,
                    re.DOTALL,
                )
                if desc_match:
                    exp_data["description"] = desc_match.group(1).strip()

                # Highlights
                highlights_match = re.search(
                    r"\*\*Highlights:\*\*\n(.+?)(?=\n\*\*Skills|\n---|\Z)",
                    entry,
                    re.DOTALL,
                )
                if highlights_match:
                    highlights = re.findall(
                        r"^- (.+)$", highlights_match.group(1), re.MULTILINE
                    )
                    exp_data["highlights"] = highlights

                # Skills (comma-separated list)
                skills_match = re.search(r"\*\*Skills:\*\* (.+)", entry)
                if skills_match:
                    skills_str = skills_match.group(1).strip()
                    skills = [s.strip() for s in skills_str.split(",")]
                    exp_data["skills"] = skills

                if exp_data:
                    experience.append(exp_data)

        # Parse Preferences section
        preferences = {}

        pref_section_match = re.search(r"## Preferences\n\n(.+)", content, re.DOTALL)
        if pref_section_match:
            pref_content = pref_section_match.group(1)

            # Tools
            tools_match = re.search(
                r"### Tools\n(.+?)(?=\n###|\n---|\Z)", pref_content, re.DOTALL
            )
            if tools_match:
                preferences["tools"] = tools_match.group(1).strip()

            # Work Style
            workstyle_match = re.search(
                r"### Work Style\n(.+?)(?=\n###|\n---|\Z)", pref_content, re.DOTALL
            )
            if workstyle_match:
                workstyle_items = re.findall(
                    r"^- (.+)$", workstyle_match.group(1), re.MULTILINE
                )
                preferences["workStyle"] = workstyle_items

            # Interests
            interests_match = re.search(
                r"### Interests\n(.+?)(?=\n---|\Z)", pref_content, re.DOTALL
            )
            if interests_match:
                interests_items = re.findall(
                    r"^- (.+)$", interests_match.group(1), re.MULTILINE
                )
                preferences["interests"] = interests_items

        return {
            "meta": meta,
            "summary": summary,
            "experience": experience,
            "preferences": preferences,
        }

    def save_career_json(self, data: dict, output_file: Path = None):
        """Save parsed data to career.json"""
        if output_file is None:
            output_file = self.content_dir / "career.json"

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✓ Parsed career history from markdown")
        print(f"  Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse career.md to JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input markdown file (default: content/career.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file (default: content/career.json)",
    )
    parser.add_argument(
        "--preview", action="store_true", help="Preview output without writing files"
    )

    args = parser.parse_args()

    md_parser = CareerMarkdownParser()

    print("Career Markdown Parser")
    print("=" * 50)
    print("")

    data = md_parser.parse_career(args.input)

    if args.preview:
        print("Preview mode - would create career.json with:")
        print("")
        print(json.dumps(data, indent=2))
    else:
        md_parser.save_career_json(data, args.output)
        print("")
        print(f"Experience entries: {len(data['experience'])}")
        print(f"Specialties: {len(data['summary'].get('specialties', []))}")
        print(
            f"Current stack categories: {len(data['summary'].get('currentStack', {}))}"
        )
