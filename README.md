# 🎬 Little Steps - YouTube Videos Feed

Automated service that fetches all video URLs from:
- **@FairyTales.English** (`Fairy Tales and Stories for Kids`)
- **@MrBookandMeStories** (`Mr Book and Me Stories`)

Runs automatically **once every 24 hours** via GitHub Actions, and maintains a **single JSON file** (`youtube_videos.json`) for your mobile application.

---

## 📁 Repository Structure

```text
your-repository-root/
│
├── .github/
│   └── workflows/
│       └── daily_fetch.yml        # ⏰ Runs every 24 hours on GitHub Actions
│
├── fetch_videos.py                # 🐍 Python script that extracts all YouTube video URLs
├── requirements.txt               # 📦 Dependencies (yt-dlp)
├── .gitignore                     # 🚫 Git ignore file
├── README.md                      # 📖 Documentation
│
└── youtube_videos.json            # 🌟 THE SINGLE JSON FILE (Contains all video URLs)
```

---

## 📱 How to Fetch in Your App (iOS & Android)

Your mobile app can fetch the latest video JSON 24/7 directly via GitHub's raw URL:

```
https://raw.githubusercontent.com/<YOUR-GITHUB-USERNAME>/<YOUR-REPO-NAME>/main/youtube_videos.json
```

### JSON Structure
```json
{
  "last_updated": "2026-10-18T05:05:31.220825+00:00",
  "total_videos": 704,
  "channels": [
    "@FairyTales.English",
    "@MrBookandMeStories"
  ],
  "videos": [
    {
      "id": "HbDh9LU1tXM",
      "title": "Puss in boots + The Lost Dragon 🐈🐉 | Fairy Tales and Stories for Kids",
      "video_url": "https://www.youtube.com/watch?v=HbDh9LU1tXM",
      "embed_url": "https://www.youtube.com/embed/HbDh9LU1tXM",
      "thumbnail_url": "https://i.ytimg.com/vi/HbDh9LU1tXM/hq720.jpg",
      "thumbnail_hq": "https://i.ytimg.com/vi/HbDh9LU1tXM/hqdefault.jpg",
      "duration": "17:53",
      "duration_seconds": 1073,
      "views": 1500,
      "channel_name": "Fairy Tales and Stories for Kids",
      "channel_handle": "@FairyTales.English"
    }
  ]
}
```

---

## 🚀 How to Upload to GitHub

In your Terminal, run:

```bash
cd "/Users/luv/Downloads/Quantocore Solutions/Little Steps/YouTube_Story_Fetcher"

# 1. Add your remote GitHub repo URL:
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git

# 2. Push to GitHub:
git push -u origin main
```

> [!IMPORTANT]
> **Enable Workflow Permissions on GitHub**:
> In your repository on GitHub:
> Go to **Settings** ➔ **Actions** ➔ **General** ➔ scroll to **Workflow permissions** ➔ select **Read and write permissions** ➔ click **Save**.
