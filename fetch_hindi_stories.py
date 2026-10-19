#!/usr/bin/env python3
"""
Hindi Stories & Rhymes Fetcher for LittleSteps
Fetches all video URLs from @infobellshindirhymes
Outputs a structured JSON file: hindi_stories.json
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime, timezone

# Target YouTube Channels for Hindi Stories & Rhymes
CHANNELS = [
    {
        "name": "Infobells - Hindi",
        "handle": "@infobellshindirhymes",
        "url": "https://www.youtube.com/@infobellshindirhymes/videos"
    }
]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON_PATH = os.path.join(OUTPUT_DIR, "hindi_stories.json")


def find_yt_dlp_executable():
    """Locate yt-dlp binary across common environments."""
    # Check virtualenv in scratch if available
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


def format_duration(seconds):
    """Format seconds into MM:SS or HH:MM:SS."""
    if not seconds or seconds <= 0:
        return ""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def fetch_channel_videos(channel_info, yt_dlp_bin):
    """Fetch video entries from a channel via yt-dlp."""
    print(f"Fetching all videos from {channel_info['handle']} ({channel_info['name']})...")
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
        print(f"Error: Could not execute '{yt_dlp_bin}'. Make sure yt-dlp is installed (pip install yt-dlp).")
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
            duration_sec = item.get("duration") or 0
            duration_str = item.get("duration_string") or format_duration(duration_sec)
            view_count = item.get("view_count") or 0

            # Find best thumbnail
            thumbs = item.get("thumbnails") or []
            best_thumb = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            if thumbs:
                best_thumb = thumbs[-1].get("url", best_thumb)

            video_record = {
                "id": video_id,
                "title": title,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "thumbnail_url": best_thumb,
                "thumbnail_hq": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "duration": duration_str,
                "duration_seconds": int(duration_sec) if duration_sec else 0,
                "views": int(view_count) if view_count else 0,
                "channel_name": channel_info["name"],
                "channel_handle": channel_info["handle"]
            }
            videos.append(video_record)
        except Exception as e:
            continue

    proc.wait()
    elapsed = time.time() - start_time
    print(f"-> Successfully extracted {len(videos)} videos from {channel_info['handle']} in {elapsed:.2f}s")
    return videos


def main():
    target_output = sys.argv[1] if len(sys.argv) > 1 else OUTPUT_JSON_PATH
    print(f"Starting Hindi stories fetch at {datetime.now(timezone.utc).isoformat()}...")
    yt_dlp_bin = find_yt_dlp_executable()
    print(f"Using yt-dlp: {yt_dlp_bin}")

    all_videos = []

    for ch in CHANNELS:
        videos = fetch_channel_videos(ch, yt_dlp_bin)
        all_videos.extend(videos)

    output_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_videos": len(all_videos),
        "channels": [ch["handle"] for ch in CHANNELS],
        "videos": all_videos
    }

    os.makedirs(os.path.dirname(os.path.abspath(target_output)), exist_ok=True)
    with open(target_output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n=======================================================")
    print(f"SUCCESS: Generated separate JSON for Hindi stories with {len(all_videos)} videos:")
    print(f"{target_output}")
    print(f"=======================================================")


if __name__ == "__main__":
    main()
