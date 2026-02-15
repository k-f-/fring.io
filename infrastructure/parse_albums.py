#!/usr/bin/env python3
"""
Parse albums.md and regenerate albums.json
Supports round-trip conversion: JSON → MD → JSON (lossless)

Usage:
    # Parse and update albums.json
    ./parse_albums.py

    # Preview without writing
    ./parse_albums.py --preview
"""

import re
import json
from datetime import datetime
from pathlib import Path
import argparse


class MarkdownToJSONParser:
    """Parse fring.io Markdown data back to JSON"""

    def __init__(self, content_dir: Path = Path("content")):
        self.content_dir = content_dir

    def parse_albums(self, input_file: Path = None) -> dict:
        """Parse albums.md to JSON structure"""
        if input_file is None:
            input_file = self.content_dir / "albums.md"

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
                "description": "Album listening log for fring.io - version agnostic content",
            }

        # Update lastUpdated
        meta["lastUpdated"] = datetime.now().isoformat()

        albums = []

        # Split into album entries (### [Date] Artist - Album)
        # Pattern: ### [2019-10-21] The Jackson 5 - Gold
        entry_pattern = r"### \[(\d{4}-\d{2}-\d{2})\] (.+?) - (.+?)\n"
        entries = re.split(entry_pattern, content)

        # Process entries in groups of 4 (split, date, artist, album, content)
        for i in range(1, len(entries), 4):
            if i + 3 > len(entries):
                break

            listened_date = entries[i]  # "2019-10-21"
            artist = entries[i + 1]
            album = entries[i + 2]
            entry_content = entries[i + 3] if i + 3 < len(entries) else ""

            # Extract metadata from entry
            album_data = {
                "listenedDate": listened_date,
                "artist": artist,
                "album": album,
                "releaseYear": None,
                "spotifyUrl": None,
                "spotifyId": None,
                "tracks": None,
                "playtime": None,
                "notes": None,
                "dateAdded": datetime.now().isoformat(),
            }

            # Released year
            release_match = re.search(r"\*\*Released:\*\* (\d{4})", entry_content)
            if release_match:
                album_data["releaseYear"] = int(release_match.group(1))

            # Spotify URL
            spotify_match = re.search(
                r"\*\*Listen:\*\* \[Spotify\]\((.+?)\)", entry_content
            )
            if spotify_match:
                spotify_url = spotify_match.group(1)
                album_data["spotifyUrl"] = spotify_url
                # Extract Spotify ID
                spotify_id_match = re.search(r"/album/([a-zA-Z0-9]+)", spotify_url)
                if spotify_id_match:
                    album_data["spotifyId"] = spotify_id_match.group(1)

            # Duration (tracks and playtime)
            duration_match = re.search(r"\*\*Duration:\*\* (.+?)\n", entry_content)
            if duration_match:
                duration_str = duration_match.group(1)
                # Parse "36 tracks, 2 hr 13 min." or "10 tracks, 34 min."
                tracks_match = re.search(r"(\d+) tracks?", duration_str)
                if tracks_match:
                    album_data["tracks"] = int(tracks_match.group(1))
                # Extract playtime (everything after tracks)
                playtime_match = re.search(r"tracks?, (.+)", duration_str)
                if playtime_match:
                    album_data["playtime"] = playtime_match.group(1).strip()

            # Notes (everything after Duration until next heading or end)
            notes_match = re.search(
                r"\*\*Duration:\*\*.*?\n\n(.+?)(?:\n\n###|\n\n---|\Z)",
                entry_content,
                re.DOTALL,
            )
            if notes_match:
                notes = notes_match.group(1).strip()
                # Strip year section headings (## 2019 ...) that bleed in
                notes = re.sub(r"##\s+\d{4}.*", "", notes, flags=re.DOTALL).strip()
                if notes:
                    album_data["notes"] = notes
            else:
                # Check for notes without Duration field
                notes_match = re.search(
                    r"\*\*Listen:\*\*.*?\n\n(.+?)(?:\n\n###|\n\n---|\Z)",
                    entry_content,
                    re.DOTALL,
                )
                if notes_match:
                    notes = notes_match.group(1).strip()
                    notes = re.sub(r"##\s+\d{4}.*", "", notes, flags=re.DOTALL).strip()
                    if notes and not notes.startswith("**Duration:**"):
                        album_data["notes"] = notes

            albums.append(album_data)

        # Sort by listened date (newest first)
        albums.sort(key=lambda x: x.get("listenedDate", ""), reverse=True)

        return {"meta": meta, "albums": albums}

    def save_albums_json(self, data: dict, output_file: Path = None):
        """Save parsed data to albums.json"""
        if output_file is None:
            output_file = self.content_dir / "albums.json"

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✓ Parsed {len(data['albums'])} albums from markdown")
        print(f"  Saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse albums.md to JSON")
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input markdown file (default: content/albums.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON file (default: content/albums.json)",
    )
    parser.add_argument(
        "--preview", action="store_true", help="Preview output without writing files"
    )

    args = parser.parse_args()

    md_parser = MarkdownToJSONParser()

    print("Albums Markdown Parser")
    print("=" * 50)
    print("")

    data = md_parser.parse_albums(args.input)

    if args.preview:
        print("Preview mode - would create albums.json with:")
        print("")
        print(json.dumps(data, indent=2))
        print("")
        print(f"Total albums: {len(data['albums'])}")
    else:
        md_parser.save_albums_json(data, args.output)
        print("")
        print("Sample albums:")
        for album in data["albums"][:3]:
            print(
                f"  • {album['artist']} - {album['album']} ({album.get('listenedDate', 'unknown')})"
            )
