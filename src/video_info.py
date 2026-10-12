"""
===========================================================
Project : Kisan Mitra AI
File    : video_info.py
Purpose : Load educational videos according to disease.
===========================================================
"""

import json
from pathlib import Path


# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

VIDEO_DATABASE_FILE = (
    BASE_DIR
    / "video_database"
    / "videos.json"
)


# =========================================================
# LOAD VIDEO DATABASE
# =========================================================

def load_video_database():

    if not VIDEO_DATABASE_FILE.exists():

        raise FileNotFoundError(
            f"Video database not found:\n"
            f"{VIDEO_DATABASE_FILE}"
        )

    with open(
        VIDEO_DATABASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        database = json.load(file)

    return database


# =========================================================
# GET VIDEOS FOR DISEASE
# =========================================================

def get_videos_for_disease(disease_id):

    database = load_video_database()

    videos = []

    for video_id, video in database.items():

        disease_ids = video.get(
            "disease_ids",
            []
        )

        if disease_id in disease_ids:

            record = video.copy()

            record["video_id"] = video_id

            videos.append(record)

    return videos


# =========================================================
# DISPLAY VIDEOS
# =========================================================

def display_videos(disease_id):

    videos = get_videos_for_disease(
        disease_id
    )

    print("\n" + "=" * 60)
    print("🎥 EDUCATIONAL VIDEOS")
    print("=" * 60)

    if not videos:

        print(
            "ℹ️ No educational videos "
            "available for this disease."
        )

        return

    for video in videos:

        print(
            f"\n🎬 {video['video_id']} - "
            f"{video['title']}"
        )

        print(
            f"   🌾 Crop      : "
            f"{video.get('crop', 'N/A')}"
        )

        print(
            f"   📂 Category  : "
            f"{video.get('category', 'N/A')}"
        )

        print(
            f"   🗣️ Language  : "
            f"{video.get('language', 'N/A')}"
        )

        print(
            f"   🏢 Source    : "
            f"{video.get('source_name') or 'Not added yet'}"
        )

        video_url = video.get(
            "video_url",
            ""
        )

        if video_url:

            print(
                f"   🔗 Video     : {video_url}"
            )

        else:

            print(
                "   🔗 Video     : "
                "Verified video will be added"
            )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "🌱 KISAN MITRA AI - "
        "VIDEO DATABASE TEST"
    )

    print("=" * 60)

    database = load_video_database()

    print(
        "\n✅ Video Database "
        "Loaded Successfully"
    )

    print(
        f"📊 Total Video Records : "
        f"{len(database)}"
    )

    test_disease = (
        "Tomato___Late_blight"
    )

    print(
        f"\n🔍 Testing Disease : "
        f"{test_disease}"
    )

    display_videos(
        test_disease
    )

    print("\n" + "=" * 60)

    print(
        "🎉 VIDEO DATABASE "
        "TEST COMPLETED!"
    )

    print("=" * 60)