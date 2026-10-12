"""
===========================================================
Project : Kisan Mitra AI
File    : video_database.py
Purpose : Fetch and store disease-specific YouTube videos.
===========================================================
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

VIDEO_DATABASE_DIR = BASE_DIR / "video_database"
VIDEO_DATABASE_FILE = VIDEO_DATABASE_DIR / "videos.json"


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv(BASE_DIR / ".env")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3/search"


# ---------------------------------------------------------
# Database helpers
# ---------------------------------------------------------

def load_video_database():
    """
    Load videos.json.
    """

    VIDEO_DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not VIDEO_DATABASE_FILE.exists():
        return {}

    try:

        with open(
            VIDEO_DATABASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return {}


def save_video_database(database):
    """
    Save video database to JSON.
    """

    VIDEO_DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        VIDEO_DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            database,
            file,
            ensure_ascii=False,
            indent=4
        )


# ---------------------------------------------------------
# YouTube search
# ---------------------------------------------------------

def fetch_youtube_videos(
    disease,
    crop,
    language="Hindi",
    max_results=5
):
    """
    Fetch disease-specific public YouTube videos.
    """

    if not YOUTUBE_API_KEY:

        raise RuntimeError(
            "YOUTUBE_API_KEY not found in .env"
        )

    query = (
        f"{crop} {disease} "
        f"treatment prevention "
        f"{language}"
    )

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": "relevance",
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(
        YOUTUBE_API_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    videos = []

    for item in data.get("items", []):

        video_id = item["id"].get("videoId")

        if not video_id:
            continue

        snippet = item["snippet"]

        videos.append({

            "video_id": video_id,

            "title": snippet.get(
                "title",
                ""
            ),

            "channel": snippet.get(
                "channelTitle",
                ""
            ),

            "published_at": snippet.get(
                "publishedAt",
                ""
            ),

            "description": snippet.get(
                "description",
                ""
            ),

            "thumbnail": snippet
            .get("thumbnails", {})
            .get("high", {})
            .get("url", ""),

            "url":
                f"https://www.youtube.com/watch?v={video_id}"

        })

    return videos


# ---------------------------------------------------------
# Add disease videos
# ---------------------------------------------------------

def add_disease_videos(
    disease_key,
    disease_name,
    crop,
    language="Hindi",
    max_results=5
):
    """
    Fetch and store videos for one disease.
    """

    print("\n" + "=" * 65)
    print("🎬 KISAN MITRA AI - VIDEO DATABASE")
    print("=" * 65)

    print(f"\n🌾 Crop    : {crop}")
    print(f"🦠 Disease : {disease_name}")
    print("🔎 Searching YouTube...")

    videos = fetch_youtube_videos(
        disease=disease_name,
        crop=crop,
        language=language,
        max_results=max_results
    )

    database = load_video_database()

    database[disease_key] = {

        "disease": disease_name,

        "crop": crop,

        "language": language,

        "source": "YouTube Data API v3",

        "videos": videos

    }

    save_video_database(database)

    print(
        f"\n✅ {len(videos)} videos saved!"
    )

    print(
        f"💾 Database: {VIDEO_DATABASE_FILE}"
    )

    return videos


# ---------------------------------------------------------
# Get videos
# ---------------------------------------------------------

def get_disease_videos(disease_key):
    """
    Return cached videos for a disease.
    """

    database = load_video_database()

    disease_data = database.get(
        disease_key
    )

    if not disease_data:
        return []

    return disease_data.get(
        "videos",
        []
    )


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

def main():

    disease_key = "Tomato___Late_blight"

    disease_name = "Late Blight"

    crop = "Tomato"

    videos = add_disease_videos(
        disease_key=disease_key,
        disease_name=disease_name,
        crop=crop,
        language="Hindi",
        max_results=5
    )

    print("\n" + "-" * 65)
    print("🎬 SAVED VIDEOS")
    print("-" * 65)

    for index, video in enumerate(
        videos,
        start=1
    ):

        print(
            f"\n{index}. "
            f"{video['title']}"
        )

        print(
            f"   📺 {video['channel']}"
        )

        print(
            f"   🔗 {video['url']}"
        )

    print("\n" + "=" * 65)
    print("✅ VIDEO DATABASE TEST COMPLETED!")
    print("=" * 65)


if __name__ == "__main__":
    main()