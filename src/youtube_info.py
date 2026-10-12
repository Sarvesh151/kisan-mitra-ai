"""
===========================================================
Project : Kisan Mitra AI
File    : youtube_info.py
Purpose : Fetch disease-specific YouTube videos
          using the official YouTube Data API v3.
===========================================================
"""

import os
import sys
import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    print("❌ ERROR: YOUTUBE_API_KEY not found in .env")
    sys.exit(1)


# ---------------------------------------------------------
# YouTube API settings
# ---------------------------------------------------------
API_URL = "https://www.googleapis.com/youtube/v3/search"


def search_youtube_videos(
    disease,
    crop="Tomato",
    language="Hindi",
    max_results=5
):
    """
    Search YouTube for disease-specific videos.
    """

    query = f"{crop} {disease} treatment prevention {language}"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "relevance",
        "key": API_KEY
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        videos = []

        for item in data.get("items", []):

            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            video = {
                "video_id": video_id,
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "published_at": snippet["publishedAt"],
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }

            videos.append(video)

        return videos

    except requests.exceptions.RequestException as error:

        print(f"❌ YouTube API Error: {error}")

        return []


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------
def main():

    print("=" * 65)
    print("🌱 KISAN MITRA AI - YOUTUBE API TEST")
    print("=" * 65)

    crop = "Tomato"
    disease = "Late Blight"

    print(f"\n🌾 Crop    : {crop}")
    print(f"🦠 Disease : {disease}")
    print("🔎 Searching YouTube...\n")

    videos = search_youtube_videos(
        disease=disease,
        crop=crop,
        language="Hindi",
        max_results=5
    )

    if not videos:

        print("❌ No videos found.")
        return

    print("=" * 65)
    print(f"🎬 {len(videos)} VIDEOS FOUND")
    print("=" * 65)

    for index, video in enumerate(videos, start=1):

        print(f"\n🎬 Video {index}")
        print(f"   Title   : {video['title']}")
        print(f"   Channel : {video['channel']}")
        print(f"   URL     : {video['url']}")


if __name__ == "__main__":
    main()