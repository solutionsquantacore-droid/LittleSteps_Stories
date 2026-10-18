#!/usr/bin/env python3
"""
YouTube Video URL Fetcher for Mobile Apps
Fetches all video URLs from @FairyTales.English and @MrBookandMeStories
Outputs a SINGLE JSON file: youtube_videos.json
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone

# Target YouTube Channels
CHANNELS = [
    {
        "name": "Fairy Tales and Stories for Kids",
        "handle": "@FairyTales.English",
        "url": "https://www.youtube.com/@FairyTales.English/videos"
    },
    {
        "name": "Mr Book and Me Stories",
        "handle": "@MrBookandMeStories",
        "url": "https://www.youtube.com/@MrBookandMeStories/videos"
    }
]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON_PATH = os.path.join(OUTPUT_DIR, "youtube_videos.json")


def find_yt_dlp_executable():
    """Locate yt-dlp binary."""
    scratch_venv = "/Users/luv/.gemini/antigravity/scratch/venv/bin/yt-dlp"
    if os.path.isfile(scratch_venv) and os.access(scratch_venv, os.X_OK):
        return scratch_venv

    python_dir = os.path.dirname(sys.executable)
    yt_dlp_path = os.path.join(python_dir, "yt-dlp")
    if os.path.isfile(yt_dlp_path) and os.access(yt_dlp_path, os.X_OK):
        return yt_dlp_path

    for p in os.environ.get("PATH", "").split(os.path.pathsep):
        candidate = os.path.join(p, "yt-dlp")
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate

    return "yt-dlp"


def fetch_channel_videos(channel_info, yt_dlp_bin):
    """Fetch video URLs from a channel."""
    print(f"Fetching videos from {channel_info['handle']}...")
    start_time = time.time()

    cmd = [
        yt_dlp_bin,
        "--flat-playlist",
        "--dump-json",
        "--no-warnings",
        "--ignore-errors",
        channel_info["url"]
    ]

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    except FileNotFoundError:
        print(f"Error: Could not execute '{yt_dlp_bin}'.")
        return []

    videos = []
    seen_ids = set()

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
            video_id = item.get("id")
            if not video_id or video_id in seen_ids:
                continue
            seen_ids.add(video_id)

            title = item.get("title", "").strip()
            duration_sec = item.get("duration")
            duration_str = item.get("duration_string") or ""
            view_count = item.get("view_count")

            # High quality thumbnail with fallback
            thumbs = item.get("thumbnails") or []
            best_thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            if thumbs:
                best_thumb = thumbs[-1].get("url", best_thumb)

            video_record = {
                "id": video_id,
                "title": title,
                "video_url": f"https://www.youtube.com/watch?v=k",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "thumbnail_url": best_thumb,
                "thumbnail_hq": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "duration": duration_str,
                "duration_seconds": duration_sec,
                "views": view_count,
                "channel_name": channel_info["name"],
                "channel_handle": channel_info["handle"]
            }
            # Fix video_url template
            video_record["video_url"] = f"https://www.youtube.com/watch?v={video_id}"
            videos.append(video_record)
        except Exception:
            continue

    proc.wait()
    elapsed = time.time() - start_time
    print(f"-> Extracted {len(videos)} videos from {channel_info['handle']} ({elapsed:.2f}s)")
    return videos


def main():
    print(f"Starting fetch at {datetime.now(timezone.utc).isoformat()}...")
    yt_dlp_bin = find_yt_dlp_executable()
    print(f"Using yt-dlp: {yt_dlp_bin}")

    all_videos = []

    for ch in CHANNELS:
        videos = fetch_channel_videos(ch, yt_dlp_bin)
        all_videos.extend(videos)

    # Output SINGLE JSON file
    output_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_videos": len(all_videos),
        "channels": [ch["handle"] for ch in CHANNELS],
        "videos": all_videos
    }

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n=======================================================")
    print(f"SUCCESS: Generated single JSON file with {len(all_videos)} video URLs:")
    print(f"{OUTPUT_JSON_PATH}")
    print(f"=======================================================")


if __name__ == "__main__":
    main()
