#!/usr/bin/env python3
"""
Fetch album artwork URLs from Spotify oEmbed API
Adds thumbnailUrl field to albums.json
"""

import json
import urllib.request
import urllib.parse
import time
from pathlib import Path

def fetch_album_art_url(spotify_url):
    """Fetch thumbnail URL from Spotify oEmbed API"""
    # URL encode the Spotify URL
    encoded_url = urllib.parse.quote(spotify_url, safe='')
    oembed_url = f"https://open.spotify.com/oembed?url={encoded_url}"

    try:
        with urllib.request.urlopen(oembed_url) as response:
            data = json.loads(response.read())
            return data.get('thumbnail_url')
    except Exception as e:
        print(f"Error fetching {spotify_url}: {e}")
        return None

def main():
    # Load albums.json
    albums_path = Path('../content/albums.json')

    with open(albums_path, 'r') as f:
        data = json.load(f)

    print(f"Fetching artwork for {len(data['albums'])} albums...")

    # Fetch artwork for each album
    updated = 0
    for i, album in enumerate(data['albums'], 1):
        spotify_url = album.get('spotifyUrl')

        if not spotify_url:
            print(f"  [{i}/{len(data['albums'])}] Skipping {album['artist']} - {album['album']} (no Spotify URL)")
            continue

        # Check if we already have a thumbnail
        if 'thumbnailUrl' in album and album['thumbnailUrl']:
            print(f"  [{i}/{len(data['albums'])}] Already have artwork for {album['artist']} - {album['album']}")
            continue

        print(f"  [{i}/{len(data['albums'])}] Fetching {album['artist']} - {album['album']}...")
        thumbnail_url = fetch_album_art_url(spotify_url)

        if thumbnail_url:
            album['thumbnailUrl'] = thumbnail_url
            updated += 1
            print(f"      ✓ Got: {thumbnail_url}")
        else:
            print(f"      ✗ Failed to fetch")

        # Be nice to Spotify's API
        time.sleep(0.5)

    # Save updated data
    if updated > 0:
        with open(albums_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Updated {updated} albums with artwork URLs")
        print(f"✓ Saved to {albums_path}")
    else:
        print("\nNo updates needed - all albums already have artwork URLs")

if __name__ == "__main__":
    main()
