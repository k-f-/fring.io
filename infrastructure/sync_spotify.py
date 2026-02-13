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

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print("Error: spotipy not installed. Run: pip install spotipy")
    sys.exit(1)

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_PLAYLIST_ID = os.environ.get("SPOTIFY_PLAYLIST_ID", "")

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


def fetch_playlist_albums(sp):
    print(f"Fetching playlist: {SPOTIFY_PLAYLIST_ID}")

    albums_seen = {}
    offset = 0
    limit = 100

    while True:
        results = sp.playlist_items(
            SPOTIFY_PLAYLIST_ID,
            offset=offset,
            limit=limit,
            fields="items(added_at,track(album(id,name,artists,release_date,total_tracks,images,external_urls))),next",
        )

        items = results.get("items", [])
        if not items:
            break

        for item in items:
            track = item.get("track")
            if not track or not track.get("album"):
                continue

            album = track["album"]
            album_id = album.get("id")
            if not album_id or album_id in albums_seen:
                continue

            artists = album.get("artists", [])
            artist_name = artists[0]["name"] if artists else "Unknown Artist"

            # release_date can be YYYY, YYYY-MM, or YYYY-MM-DD
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

            # added_at = when track was added to playlist, used as listenedDate
            added_at = item.get("added_at", "")
            listened_date = (
                added_at[:10] if added_at else datetime.now().strftime("%Y-%m-%d")
            )

            albums_seen[album_id] = {
                "listenedDate": listened_date,
                "artist": artist_name,
                "album": album["name"],
                "releaseYear": release_year,
                "spotifyUrl": spotify_url,
                "spotifyId": album_id,
                "tracks": album.get("total_tracks"),
                "thumbnailUrl": thumbnail_url,
            }

        if not results.get("next"):
            break
        offset += limit

    print(f"  Found {len(albums_seen)} unique albums in playlist")
    return albums_seen


def fetch_album_durations(sp, album_ids):
    durations = {}
    ids_list = list(album_ids)

    for i in range(0, len(ids_list), 20):
        batch = ids_list[i : i + 20]
        results = sp.albums(batch)

        for album_data in results.get("albums", []):
            if not album_data:
                continue
            album_id = album_data["id"]
            total_ms = sum(
                t.get("duration_ms", 0)
                for t in album_data.get("tracks", {}).get("items", [])
            )
            total_min = round(total_ms / 60000)
            if total_min >= 60:
                hours = total_min // 60
                mins = total_min % 60
                durations[album_id] = f"{hours} hr {mins} min."
            else:
                durations[album_id] = f"{total_min} min."

    return durations


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
    for aid in new_album_ids:
        a = playlist_albums[aid]
        print(f"  + {a['artist']} - {a['album']} ({a['listenedDate']})")

    print("\nFetching album durations...")
    durations = fetch_album_durations(sp, new_album_ids)

    new_albums = []
    for aid in new_album_ids:
        album = playlist_albums[aid]
        album["playtime"] = durations.get(aid, None)
        new_albums.append(album)

    prepend_albums_to_md(new_albums)


if __name__ == "__main__":
    main()
