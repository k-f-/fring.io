#!/usr/bin/env python3
"""
Extract albums from old_life_org.md and create initial albums.json

This is a ONE-TIME migration script to pull the 27 albums from the
old org-mode file into the new JSON structure.

Usage:
    ./migrate_albums.py
    ./migrate_albums.py --preview  # Don't write, just show output
"""

import re
import json
from datetime import datetime
from pathlib import Path
import argparse


def parse_album_entry(text):
    """Parse markdown album entry into dict"""
    # Extract header: ### [2019-10-21 Mon] Artist - Album
    header_match = re.search(r'###\s+\[(\d{4}-\d{2}-\d{2})\s+\w+\]\s+(.+?)\s+-\s+(.+)', text)

    if not header_match:
        return None

    listened_date = header_match.group(1)
    artist = header_match.group(2).strip()
    album = header_match.group(3).strip()

    # Extract metadata
    release_match = re.search(r'-\s+Release:\s+(\d{4})', text)
    spotify_match = re.search(r'-\s+Link:\s+\[Spotify\]\((.+?)\)', text)
    tracks_match = re.search(r'-\s+Tracks:\s+(\d+)', text)
    playtime_match = re.search(r'-\s+Playtime:\s+(.+?)(?:\n|$)', text, re.MULTILINE)

    # Extract notes (last bullet point without a colon)
    notes_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('-') and ':' not in line:
            notes_lines.append(line[1:].strip())

    notes = ' '.join(notes_lines) if notes_lines else None

    # Extract Spotify ID from URL
    spotify_id = None
    if spotify_match:
        spotify_url = spotify_match.group(1)
        spotify_id_match = re.search(r'/album/([a-zA-Z0-9]+)', spotify_url)
        if spotify_id_match:
            spotify_id = spotify_id_match.group(1)

    album_data = {
        "listenedDate": listened_date,
        "artist": artist,
        "album": album,
        "releaseYear": int(release_match.group(1)) if release_match else None,
        "spotifyUrl": spotify_match.group(1) if spotify_match else None,
        "spotifyId": spotify_id,
        "tracks": int(tracks_match.group(1)) if tracks_match else None,
        "playtime": playtime_match.group(1).strip() if playtime_match else None,
        "notes": notes,
        "dateAdded": datetime.now().isoformat()
    }

    return album_data


def migrate_albums(preview=False):
    """Extract albums from old_life_org.md"""
    org_file = Path.home() / "Documents/Code/old_life_org.md"

    if not org_file.exists():
        print(f"❌ Source file not found: {org_file}")
        print("   Please check the path to old_life_org.md")
        return

    # Read markdown file
    with open(org_file, 'r') as f:
        content = f.read()

    # Find Albums section
    albums_section = re.search(r'^# Albums\n(.+?)(?=^# |\Z)', content, re.MULTILINE | re.DOTALL)

    if not albums_section:
        print("❌ No Albums section found in markdown file")
        return

    section_text = albums_section.group(1)

    # Split by ### headers
    entries = re.split(r'(?=^### \[)', section_text, flags=re.MULTILINE)

    albums = []
    for entry in entries:
        if entry.strip().startswith('###'):
            album_data = parse_album_entry(entry)
            if album_data:
                albums.append(album_data)

    # Sort by listened date (newest first)
    albums.sort(key=lambda x: x['listenedDate'], reverse=True)

    # Create JSON output
    output = {
        "meta": {
            "version": "1.0",
            "lastUpdated": datetime.now().isoformat(),
            "description": "Album listening log for fring.io - version agnostic content"
        },
        "albums": albums
    }

    if preview:
        print("Preview mode - would create albums.json with:")
        print("")
        print(json.dumps(output, indent=2))
        print("")
        print(f"Total albums found: {len(albums)}")
    else:
        # Write to file
        output_file = Path("content/albums.json")
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"✓ Extracted {len(albums)} albums from old_life_org.md")
        print(f"  Saved to {output_file}")
        print("")
        print("Sample albums:")
        for album in albums[:3]:
            print(f"  • {album['artist']} - {album['album']} ({album['listenedDate']})")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Migrate albums from old_life_org.md")
    parser.add_argument("--preview", action="store_true",
                       help="Preview output without writing files")

    args = parser.parse_args()

    print("Albums Migration Script")
    print("="*50)
    print("")

    migrate_albums(preview=args.preview)
