#!/usr/bin/env python3
"""
Sync Spotify "signal playlist" with albums.md.

Reads a public Spotify playlist where each track represents an album the user
has listened to. Extracts album metadata, diffs against existing albums.json,
and prepends new entries to albums.md.

Uses Client Credentials flow (no user OAuth needed for public playlists).

Usage:
    python infrastructure/sync_spotify.py

Environment variables:
    SPOTIFY_CLIENT_ID      - Spotify app client ID
    SPOTIFY_CLIENT_SECRET  - Spotify app client secret
    SPOTIFY_PLAYLIST_ID    - Public playlist ID to poll
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print("Error: spotipy not installed. Run: pip install spotipy")
    sys.exit(1)

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
_raw_playlist_id = os.environ.get("SPOTIFY_PLAYLIST_ID", "")


def _extract_playlist_id(raw):
    """Accept URL, URI, or bare ID and return just the 22-char playlist ID."""
    if not raw:
        return ""
    # https://open.spotify.com/playlist/37i9dQ...?si=abc
    match = re.search(r"playlist[/:]([a-zA-Z0-9]+)", raw)
    if match:
        return match.group(1)
    # Already a bare ID
    return raw.split("?")[0].strip()


SPOTIFY_PLAYLIST_ID = _extract_playlist_id(_raw_playlist_id)

ALBUMS_MD = Path("content/albums.md")
ALBUMS_JSON = Path("content/albums.json")


def get_spotify_client():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET required.")
        sys.exit(1)
    if not SPOTIFY_PLAYLIST_ID:
        print("Error: SPOTIFY_PLAYLIST_ID required.")
        sys.exit(1)

    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def fetch_playlist_track_ids():
    """Scrape the embed page to get track IDs — bypasses dev mode API restrictions."""
    embed_url = f"https://open.spotify.com/embed/playlist/{SPOTIFY_PLAYLIST_ID}"
    print(f"Fetching playlist via embed: {SPOTIFY_PLAYLIST_ID}")

    with urlopen(embed_url, timeout=30) as resp:
        html = resp.read().decode("utf-8")

    match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
    if not match:
        print("  Warning: could not parse embed page")
        return []

    data = json.loads(match.group(1))
    track_list = (
        data.get("props", {})
        .get("pageProps", {})
        .get("state", {})
        .get("data", {})
        .get("entity", {})
        .get("trackList", [])
    )

    # spotify:track:XXXXX → XXXXX
    track_ids = []
    for t in track_list:
        uri = t.get("uri", "")
        if uri.startswith("spotify:track:"):
            track_ids.append(uri.split(":")[-1])

    print(f"  Found {len(track_ids)} tracks in playlist")
    return track_ids


def fetch_playlist_albums(sp):
    """Get track IDs from embed, then look up album metadata via API.

    Uses sp.track() individually because Spotify dev mode (Feb 2026)
    returns 403 on batch endpoints (sp.tracks, sp.albums). Album metadata
    is extracted from the track response. Duration is fetched best-effort
    via sp.album() individually.
    """
    track_ids = fetch_playlist_track_ids()
    if not track_ids:
        return {}

    # Step 1: Get album metadata from individual track lookups
    albums_seen = {}
    print(f"  Looking up {len(track_ids)} tracks individually...")
    for track_id in track_ids:
        try:
            track = sp.track(track_id)
        except Exception as e:
            print(f"  Warning: failed to look up track {track_id}: {e}")
            continue

        if not track or not track.get("album"):
            continue

        album = track["album"]
        album_id = album.get("id")
        if not album_id or album_id in albums_seen:
            continue

        artists = album.get("artists", [])
        artist_name = artists[0]["name"] if artists else "Unknown Artist"

        release_date = album.get("release_date", "")
        release_year = None
        if release_date:
            try:
                release_year = int(release_date[:4])
            except (ValueError, IndexError):
                pass

        spotify_url = album.get("external_urls", {}).get("spotify", "")
        images = album.get("images", [])
        thumbnail_url = images[0]["url"] if images else None

        albums_seen[album_id] = {
            "listenedDate": datetime.now().strftime("%Y-%m-%d"),
            "artist": artist_name,
            "album": album["name"],
            "releaseYear": release_year,
            "spotifyUrl": spotify_url,
            "spotifyId": album_id,
            "tracks": album.get("total_tracks"),
            "thumbnailUrl": thumbnail_url,
            "playtime": None,
        }

    print(f"  Found {len(albums_seen)} unique albums from tracks")

    # Step 2: Try to get durations via sp.album() individually (best-effort)
    print("  Fetching album durations (best-effort)...")
    for album_id in albums_seen:
        try:
            album_data = sp.album(album_id)
            total_ms = sum(
                t.get("duration_ms", 0)
                for t in album_data.get("tracks", {}).get("items", [])
            )
            total_min = round(total_ms / 60000)
            if total_min >= 60:
                hours = total_min // 60
                mins = total_min % 60
                albums_seen[album_id]["playtime"] = f"{hours} hr {mins} min."
            else:
                albums_seen[album_id]["playtime"] = f"{total_min} min."
        except Exception as e:
            print(f"  Warning: could not fetch duration for {album_id}: {e}")

    resolved_count = sum(1 for a in albums_seen.values() if a["playtime"])
    print(f"  Resolved {len(albums_seen)} albums ({resolved_count} with durations)")
    return albums_seen


def load_existing_spotify_ids():
    if not ALBUMS_JSON.exists():
        return set()

    with open(ALBUMS_JSON) as f:
        data = json.load(f)

    return {a["spotifyId"] for a in data.get("albums", []) if a.get("spotifyId")}


def format_album_md_entry(album):
    lines = []
    lines.append(f"### [{album['listenedDate']}] {album['artist']} - {album['album']}")

    if album.get("releaseYear"):
        lines.append(f"**Released:** {album['releaseYear']}")

    if album.get("spotifyUrl"):
        lines.append(f"**Listen:** [Spotify]({album['spotifyUrl']})")

    duration_parts = []
    if album.get("tracks"):
        duration_parts.append(f"{album['tracks']} tracks")
    if album.get("playtime"):
        duration_parts.append(album["playtime"])
    if duration_parts:
        lines.append(f"**Duration:** {', '.join(duration_parts)}")

    lines.append("")

    return "\n".join(lines)


def prepend_albums_to_md(new_albums):
    if not ALBUMS_MD.exists():
        print(f"Error: {ALBUMS_MD} not found. Run from repo root.")
        sys.exit(1)

    md_content = ALBUMS_MD.read_text()

    sorted_albums = sorted(new_albums, key=lambda a: a["listenedDate"], reverse=True)

    by_year = {}
    for album in sorted_albums:
        year = album["listenedDate"][:4]
        by_year.setdefault(year, []).append(album)

    for year in sorted(by_year.keys(), reverse=True):
        albums = by_year[year]
        entries_md = "\n".join(format_album_md_entry(a) for a in albums)

        # Pattern: ## YYYY (N albums)
        year_pattern = re.compile(rf"^(## {year} \(\d+ albums?\))\s*$", re.MULTILINE)
        match = year_pattern.search(md_content)

        if match:
            existing_header = match.group(1)
            count_match = re.search(r"\((\d+) albums?\)", existing_header)
            if count_match:
                old_count = int(count_match.group(1))
                new_count = old_count + len(albums)
                new_header = f"## {year} ({new_count} albums)"
            else:
                new_header = existing_header

            insert_pos = match.end()
            md_content = (
                md_content[:insert_pos] + "\n\n" + entries_md + md_content[insert_pos:]
            )
            md_content = md_content.replace(existing_header, new_header, 1)
        else:
            first_section = re.search(r"^## \d{4}", md_content, re.MULTILINE)
            if first_section:
                insert_pos = first_section.start()
                new_section = f"## {year} ({len(albums)} albums)\n\n{entries_md}\n\n"
                md_content = (
                    md_content[:insert_pos] + new_section + md_content[insert_pos:]
                )
            else:
                md_content = (
                    md_content.rstrip()
                    + f"\n\n## {year} ({len(albums)} albums)\n\n{entries_md}\n"
                )

    ALBUMS_MD.write_text(md_content)
    print(f"\n✓ Added {len(new_albums)} album(s) to {ALBUMS_MD}")


def main():
    sp = get_spotify_client()

    playlist_albums = fetch_playlist_albums(sp)

    if not playlist_albums:
        print("\nPlaylist is empty or inaccessible.")
        return

    existing_ids = load_existing_spotify_ids()
    new_album_ids = [aid for aid in playlist_albums if aid not in existing_ids]

    if not new_album_ids:
        print("\nNo new albums found.")
        return

    print(f"\nFound {len(new_album_ids)} new album(s):")
    new_albums = []
    for aid in new_album_ids:
        a = playlist_albums[aid]
        print(f"  + {a['artist']} - {a['album']} ({a['listenedDate']})")
        new_albums.append(a)

    prepend_albums_to_md(new_albums)


if __name__ == "__main__":
    main()
