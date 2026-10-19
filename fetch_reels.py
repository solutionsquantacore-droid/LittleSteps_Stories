#!/usr/bin/env python3
"""
Kids Learning Reels Fetcher
---------------------------
Fetches YouTube Shorts from configured educational channels and outputs a
structured JSON file (kids_reels.json) ready to be hosted on GitHub.

To add or remove channels, simply edit the CHANNELS list below.
"""

import sys
import os
import json
import re
import time
import urllib.request
import urllib.error

# ==============================================================================
# CONFIGURATION: Add or remove channels here!
# ==============================================================================
CHANNELS = [
    {
        "handle": "@nursykids",
        "name": "NursyKids",
        "category": "Alphabets & Rhymes",
        "max_shorts": 100
    },
    {
        "handle": "@LucasAndFriends",
        "name": "Lucas & Friends",
        "category": "Numbers & Words",
        "max_shorts": 100
    },
    {
        "handle": "@laguanak-anak",
        "name": "LooLoo Lagu Anak",
        "category": "Songs & Shapes",
        "max_shorts": 100
    }
]

# Output file path (can be overridden with command-line argument)
DEFAULT_OUTPUT_FILE = "kids_reels.json"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def clean_handle(handle: str) -> str:
    """Ensure handle has no leading @ for URL usage."""
    return handle.lstrip("@").strip()

def clean_title(raw_title: str) -> str:
    """Clean up YouTube title by removing hashtags and messy suffixes."""
    # Remove hashtags
    title = re.sub(r'#\w+', '', raw_title).strip()
    # Split by pipe if it's very long (often channel marketing after pipe)
    if '|' in title:
        parts = [p.strip() for p in title.split('|') if p.strip()]
        if parts:
            title = parts[0]
    # Remove trailing dashes or dots
    title = re.sub(r'[-–—\.\s]+$', '', title).strip()
    return title if title else raw_title

def fetch_shorts_ids(handle: str) -> list:
    """Fetch video IDs of shorts from channel page."""
    clean_h = clean_handle(handle)
    url = f"https://www.youtube.com/@{clean_h}/shorts"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8")
        # Match /shorts/VIDEO_ID (11 chars)
        found_ids = re.findall(r'/shorts/([a-zA-Z0-9_-]{11})', html)
        # Deduplicate while preserving order
        unique_ids = list(dict.fromkeys(found_ids))
        return unique_ids
    except Exception as e:
        print(f"  [ERROR] Failed to fetch channel feed for {handle}: {e}")
        return []

def fetch_oembed_data(video_id: str) -> dict:
    """Fetch official title, author name, and thumbnail from YouTube oEmbed."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        data = urllib.request.urlopen(req, timeout=10).read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        # Fallback if oembed fails
        return {
            "title": f"Fun Learning Reel ({video_id})",
            "author_name": "Kids Learning",
            "thumbnail_url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        }

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_FILE
    print("=" * 60)
    print("  Kids Learning Reels - Channel Shorts Data Fetcher")
    print(f"  Target Output: {output_path}")
    print(f"  Channels Configured: {len(CHANNELS)}")
    print("=" * 60)

    all_reels = []
    base_likes_seed = 350

    for ch in CHANNELS:
        handle = ch["handle"]
        channel_name = ch.get("name", handle)
        max_shorts = ch.get("max_shorts", 10)

        print(f"\n🔍 Processing {handle} ({channel_name})...")
        video_ids = fetch_shorts_ids(handle)
        print(f"   Found {len(video_ids)} total Shorts in feed.")

        selected_ids = video_ids[:max_shorts]
        print(f"   Fetching details for top {len(selected_ids)} shorts...")

        channel_reels_count = 0
        for vid in selected_ids:
            time.sleep(0.15) # Gentle rate limit
            oembed = fetch_oembed_data(vid)
            full_title = oembed.get("title", "")
            short_title = clean_title(full_title)
            thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"

            base_likes_seed = (base_likes_seed * 17 + 89) % 650 + 200

            reel_item = {
                "id": vid,
                "title": short_title,
                "fullTitle": full_title,
                "channelHandle": handle,
                "channelName": channel_name,
                "thumbnailUrl": thumb,
                "initialLikes": base_likes_seed
            }
            all_reels.append(reel_item)
            channel_reels_count += 1
            print(f"   ✓ [{vid}] {short_title[:45]}...")

        print(f"   -> Added {channel_reels_count} reels for {handle}")

    # Write output JSON
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_reels, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"🎉 SUCCESS! Total {len(all_reels)} reels saved to: {output_path}")
    print("You can now commit and upload this file to your GitHub repository.")
    print("=" * 60)

if __name__ == "__main__":
    main()
