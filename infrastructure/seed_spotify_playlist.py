#!/usr/bin/env python3
"""
One-time seed script: generate track URIs from albums.json for playlist seeding.

For each album in albums.json that has a spotifyId, looks up the first track
and writes its URI to seed_tracks.txt. Copy-paste these into your Spotify
desktop app to populate the signal playlist.

Uses Client Credentials flow (no user OAuth needed — read-only).

Usage:
    python infrastructure/seed_spotify_playlist.py

Environment variables:
    SPOTIFY_CLIENT_ID      - Spotify app client ID
    SPOTIFY_CLIENT_SECRET  - Spotify app client secret
    SPOTIFY_PLAYLIST_ID    - Target playlist ID (to check what's already there)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

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
    if not raw:
        return ""
    match = re.search(r"playlist[/:]([a-zA-Z0-9]+)", raw)
    if match:
        return match.group(1)
    return raw.split("?")[0].strip()


SPOTIFY_PLAYLIST_ID = _extract_playlist_id(_raw_playlist_id)

ALBUMS_JSON = Path("content/albums.json")


def get_spotify_client():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Error: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET required.")
        sys.exit(1)

    auth_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
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
    to_add = [a for a in albums if a.get("spotifyId")]
    print(f"Found {len(to_add)} albums with Spotify IDs in albums.json")

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

    output_file = Path("seed_tracks.txt")
    output_file.write_text("\n".join(track_uris) + "\n")
    print(f"\n✓ Wrote {len(track_uris)} track URIs to {output_file}")
    print(
        "  Open your playlist in Spotify desktop, then select all + paste from this file."
    )


if __name__ == "__main__":
    main()
