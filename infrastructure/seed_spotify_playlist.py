#!/usr/bin/env python3
"""
One-time seed script: populate the Spotify signal playlist from albums.json.

For each album in albums.json that has a spotifyId, looks up the first track
and adds it to the designated playlist. Requires Authorization Code flow
(write access to user playlists) — run locally, not in CI.

Usage:
    python infrastructure/seed_spotify_playlist.py

Environment variables:
    SPOTIFY_CLIENT_ID      - Spotify app client ID
    SPOTIFY_CLIENT_SECRET  - Spotify app client secret
    SPOTIFY_PLAYLIST_ID    - Target playlist ID to populate
    SPOTIFY_REDIRECT_URI   - OAuth redirect URI (default: http://localhost:8888/callback)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError:
    print("Error: spotipy not installed. Run: pip install spotipy")
    sys.exit(1)

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.environ.get(
    "SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback"
)

_raw_playlist_id = os.environ.get("SPOTIFY_PLAYLIST_ID", "")


def _extract_playlist_id(raw):
    if not raw:
        return ""
    match = re.search(r"playlist[/:]([a-zA-Z0-9]+)", raw)
    if match:
        return match.group(1)
    return raw.split("?")[0].strip()


SPOTIFY_PLAYLIST_ID = _extract_playlist_id(_raw_playlist_id)

ALBUMS_JSON = Path("content/albums.json")

SCOPE = "playlist-modify-public playlist-modify-private"


def get_spotify_client():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET required.")
        sys.exit(1)
    if not SPOTIFY_PLAYLIST_ID:
        print("Error: SPOTIFY_PLAYLIST_ID required.")
        sys.exit(1)

    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
    )
    return spotipy.Spotify(auth_manager=auth_manager)


def load_albums():
    if not ALBUMS_JSON.exists():
        print(f"Error: {ALBUMS_JSON} not found. Run from repo root.")
        sys.exit(1)

    with open(ALBUMS_JSON) as f:
        data = json.load(f)

    return data.get("albums", [])


def get_existing_playlist_album_ids(sp):
    album_ids = set()
    offset = 0

    while True:
        results = sp.playlist_items(
            SPOTIFY_PLAYLIST_ID,
            offset=offset,
            limit=100,
            fields="items(track(album(id))),next",
        )

        for item in results.get("items", []):
            track = item.get("track")
            if track and track.get("album"):
                aid = track["album"].get("id")
                if aid:
                    album_ids.add(aid)

        if not results.get("next"):
            break
        offset += 100

    return album_ids


def get_first_track_uri(sp, album_id):
    try:
        album = sp.album(album_id)
        tracks = album.get("tracks", {}).get("items", [])
        if tracks:
            return tracks[0].get("uri")
    except Exception as e:
        print(f"  Warning: could not fetch album {album_id}: {e}")
    return None


def main():
    sp = get_spotify_client()

    albums = load_albums()
    albums_with_spotify = [a for a in albums if a.get("spotifyId")]
    print(f"Found {len(albums_with_spotify)} albums with Spotify IDs in albums.json")

    existing_ids = get_existing_playlist_album_ids(sp)
    print(f"Playlist already contains {len(existing_ids)} albums")

    to_add = [a for a in albums_with_spotify if a["spotifyId"] not in existing_ids]
    print(f"Albums to seed: {len(to_add)}")

    if not to_add:
        print("\nAll albums already in playlist. Nothing to do.")
        return

    # Sort oldest first so playlist ends up chronological (oldest added first)
    to_add.sort(key=lambda a: a.get("listenedDate", ""))

    track_uris = []
    for album in to_add:
        uri = get_first_track_uri(sp, album["spotifyId"])
        if uri:
            track_uris.append(uri)
            print(f"  + {album['artist']} - {album['album']}")
        else:
            print(f"  ✗ {album['artist']} - {album['album']} (no tracks found)")
        time.sleep(0.1)

    if not track_uris:
        print("\nNo tracks to add.")
        return

    # Spotify API allows max 100 tracks per request
    added = 0
    for i in range(0, len(track_uris), 100):
        batch = track_uris[i : i + 100]
        sp.playlist_add_items(SPOTIFY_PLAYLIST_ID, batch)
        added += len(batch)
        print(f"  Added batch: {len(batch)} tracks ({added}/{len(track_uris)})")

    print(f"\n✓ Seeded {added} tracks into playlist {SPOTIFY_PLAYLIST_ID}")


if __name__ == "__main__":
    main()
