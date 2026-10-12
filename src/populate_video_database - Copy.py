"""
===========================================================
Project : Kisan Mitra AI
File    : populate_video_database.py
Author  : Sarvesh Kumar

Purpose :
Populate the existing video_database/videos.json
using the official YouTube Data API v3.

Important:
- Only public YouTube videos are searched.
- Videos are scored for disease relevance.
- Irrelevant disease videos are rejected.
- "verified" remains False because API results
  are not automatically agricultural verification.
===========================================================
"""

import json
import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "video_database"

DATABASE_FILE = DATABASE_DIR / "videos.json"


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(BASE_DIR / ".env")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

YOUTUBE_API_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)


# =========================================================
# CHECK API KEY
# =========================================================

if not YOUTUBE_API_KEY:

    print()
    print("=" * 65)
    print("❌ ERROR: YOUTUBE_API_KEY NOT FOUND")
    print("=" * 65)
    print()
    print("Please check your .env file:")
    print()
    print("YOUTUBE_API_KEY=YOUR_API_KEY")
    print()

    raise SystemExit(1)


# =========================================================
# LOAD DATABASE
# =========================================================

def load_database():

    if not DATABASE_FILE.exists():

        print()
        print("❌ videos.json not found.")
        print()
        print(f"Expected location:")
        print(DATABASE_FILE)
        print()

        raise SystemExit(1)

    try:

        with open(
            DATABASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            database = json.load(file)

        return database

    except json.JSONDecodeError:

        print()
        print("❌ ERROR: videos.json contains invalid JSON.")
        print()

        raise SystemExit(1)


# =========================================================
# SAVE DATABASE
# =========================================================

def save_database(database):

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            database,
            file,
            ensure_ascii=False,
            indent=4
        )


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    # Replace common separators
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    text = text.replace("|", " ")
    text = text.replace("/", " ")

    # Remove extra spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# DISEASE KEYWORDS
# =========================================================

DISEASE_ALIASES = {

    "late blight": [
        "late blight",
        "late-blight",
        "phytophthora",
        "पछेती झुलसा",
        "झुलसा रोग",
        "लेट ब्लाइट"
    ],

    "early blight": [
        "early blight",
        "early-blight",
        "alternaria",
        "अगेती झुलसा",
        "अर्ली ब्लाइट"
    ],

    "leaf mold": [
        "leaf mold",
        "leaf mould",
        "cladosporium",
        "लीफ मोल्ड"
    ],

    "septoria leaf spot": [
        "septoria",
        "septoria leaf spot",
        "septoria leaf",
        "सेप्टोरिया"
    ],

    "spider mites": [
        "spider mite",
        "spider mites",
        "two spotted spider mite",
        "red spider mite",
        "स्पाइडर माइट"
    ],

    "target spot": [
        "target spot",
        "target leaf spot",
        "टारगेट स्पॉट"
    ],

    "yellow leaf curl virus": [
        "yellow leaf curl virus",
        "tomato yellow leaf curl virus",
        "tylcv",
        "leaf curl virus",
        "yellow leaf curl",
        "लीफ कर्ल वायरस"
    ],

    "tomato mosaic virus": [
        "tomato mosaic virus",
        "tomato mosaic",
        "tmv",
        "मोजेक वायरस",
        "मोजेक रोग"
    ],

    "bacterial spot": [
        "bacterial spot",
        "bacterial leaf spot",
        "xanthomonas",
        "बैक्टीरियल स्पॉट"
    ]
}


# =========================================================
# GET DISEASE ALIASES
# =========================================================

def get_disease_aliases(disease_name):

    disease_normalized = normalize_text(
        disease_name
    )

    for key, aliases in DISEASE_ALIASES.items():

        if (
            key in disease_normalized
            or disease_normalized in key
        ):

            return aliases

    # Generic fallback
    return [
        disease_normalized
    ]


# =========================================================
# SEARCH YOUTUBE
# =========================================================

def search_youtube(
    query,
    max_results=10
):

    print()
    print("🔎 YouTube Query:")
    print(f"   {query}")

    params = {

        "part": "snippet",

        "q": query,

        "type": "video",

        "maxResults": max_results,

        "order": "relevance",

        "key": YOUTUBE_API_KEY
    }

    try:

        response = requests.get(
            YOUTUBE_API_URL,
            params=params,
            timeout=20
        )

        # Show API errors clearly
        if response.status_code != 200:

            try:
                error_data = response.json()

                print()
                print("❌ YouTube API Error:")
                print(
                    error_data
                )

            except Exception:

                print()
                print(
                    "❌ YouTube API Error:"
                )

                print(
                    response.text
                )

            return []

        data = response.json()

        return data.get(
            "items",
            []
        )

    except requests.exceptions.RequestException as error:

        print()
        print(
            "❌ Network/API Error:"
        )

        print(error)

        return []


# =========================================================
# SCORE VIDEO
# =========================================================

def score_video(
    item,
    crop,
    disease_aliases,
    category
):

    video_id = item.get(
        "id",
        {}
    ).get(
        "videoId"
    )

    if not video_id:

        return None

    snippet = item.get(
        "snippet",
        {}
    )

    youtube_title = snippet.get(
        "title",
        ""
    )

    description = snippet.get(
        "description",
        ""
    )

    channel = snippet.get(
        "channelTitle",
        ""
    )

    # Combine title + description + channel
    title_text = normalize_text(
        youtube_title
    )

    description_text = normalize_text(
        description
    )

    channel_text = normalize_text(
        channel
    )

    full_text = (
        title_text
        + " "
        + description_text
        + " "
        + channel_text
    )

    score = 0

    matched_disease = False

    # -----------------------------------------------------
    # Crop matching
    # -----------------------------------------------------

    crop_normalized = normalize_text(
        crop
    )

    if crop_normalized in full_text:

        score += 5

    # -----------------------------------------------------
    # Disease matching
    # -----------------------------------------------------

    matched_aliases = []

    for alias in disease_aliases:

        alias_normalized = normalize_text(
            alias
        )

        if not alias_normalized:
            continue

        if alias_normalized in title_text:

            score += 15

            matched_disease = True

            matched_aliases.append(
                alias
            )

        elif alias_normalized in full_text:

            score += 8

            matched_disease = True

            matched_aliases.append(
                alias
            )

    # -----------------------------------------------------
    # Management keywords
    # -----------------------------------------------------

    management_keywords = [

        "treatment",
        "management",
        "control",
        "prevention",
        "disease",
        "plant disease",

        "इलाज",
        "रोकथाम",
        "नियंत्रण",
        "प्रबंधन",
        "रोग"
    ]

    for keyword in management_keywords:

        if keyword in full_text:

            score += 2

    # -----------------------------------------------------
    # Agriculture keywords
    # -----------------------------------------------------

    agriculture_keywords = [

        "farmer",
        "farming",
        "agriculture",
        "crop",
        "plant",
        "tomato",

        "किसान",
        "खेती",
        "फसल",
        "पौधा",
        "टमाटर"
    ]

    for keyword in agriculture_keywords:

        if keyword in full_text:

            score += 1

    # -----------------------------------------------------
    # Category specific scoring
    # -----------------------------------------------------

    if category == "prevention":

        prevention_keywords = [

            "prevention",
            "prevent",
            "management",
            "control",
            "sanitation",
            "disease prevention",

            "रोकथाम",
            "बचाव",
            "नियंत्रण"
        ]

        for keyword in prevention_keywords:

            if keyword in full_text:

                score += 3

    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "score": score,

        "matched_disease":
            matched_disease,

        "matched_aliases":
            matched_aliases,

        "video_id":
            video_id,

        "title":
            youtube_title,

        "channel":
            channel,

        "description":
            description,

        "published_at":
            snippet.get(
                "publishedAt",
                ""
            ),

        "thumbnail":
            snippet
            .get(
                "thumbnails",
                {}
            )
            .get(
                "high",
                {}
            )
            .get(
                "url",
                ""
            )
    }


# =========================================================
# SELECT BEST VIDEO
# =========================================================

def get_best_video(
    record
):

    title = record.get(
        "title",
        ""
    )

    crop = record.get(
        "crop",
        ""
    )

    language = record.get(
        "language",
        "Hindi"
    )

    category = record.get(
        "category",
        ""
    )

    disease_ids = record.get(
        "disease_ids",
        []
    )

    # -----------------------------------------------------
    # Determine search query
    # -----------------------------------------------------

    disease_names = []

    for disease_id in disease_ids:

        disease_name = disease_id

        disease_name = disease_name.replace(
            "___",
            " "
        )

        disease_name = disease_name.replace(
            "_",
            " "
        )

        disease_names.append(
            disease_name
        )

    # -----------------------------------------------------
    # Disease-specific record
    # -----------------------------------------------------

    if len(disease_names) == 1:

        disease_name = disease_names[0]

        query = (
            f'"{crop}" '
            f'"{disease_name}" '
            f'treatment management '
            f'{language}'
        )

        aliases = get_disease_aliases(
            disease_name
        )

        prevention_mode = False

    # -----------------------------------------------------
    # Multi-disease prevention record
    # -----------------------------------------------------

    else:

        disease_name = ""

        query = (
            f'"{crop}" '
            f'disease prevention '
            f'management '
            f'{language}'
        )

        aliases = []

        prevention_mode = True

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    results = search_youtube(
        query=query,
        max_results=10
    )

    if not results:

        return None

    candidates = []

    # -----------------------------------------------------
    # Score results
    # -----------------------------------------------------

    for item in results:

        result = score_video(
            item=item,
            crop=crop,
            disease_aliases=aliases,
            category=category
        )

        if result is None:
            continue

        # -------------------------------------------------
        # Disease-specific video
        # -------------------------------------------------

        if not prevention_mode:

            # MUST match requested disease
            if not result[
                "matched_disease"
            ]:

                print(
                    f"   ❌ Rejected: "
                    f"{result['title']}"
                )

                continue

        # -------------------------------------------------
        # Prevention video
        # -------------------------------------------------

        else:

            # For V004, disease match is not mandatory
            # because it covers multiple diseases.

            if result["score"] < 8:

                print(
                    f"   ❌ Low relevance: "
                    f"{result['title']}"
                )

                continue

        candidates.append(
            result
        )

    # -----------------------------------------------------
    # No valid candidates
    # -----------------------------------------------------

    if not candidates:

        print()
        print(
            "⚠️ No sufficiently relevant "
            "video found."
        )

        return None

    # -----------------------------------------------------
    # Sort by score
    # -----------------------------------------------------

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = candidates[0]

    # -----------------------------------------------------
    # Display selection
    # -----------------------------------------------------

    print()
    print(
        f"🏆 Best Match Score : "
        f"{best['score']}"
    )

    if best["matched_aliases"]:

        print(
            "🎯 Matched Disease : "
            + ", ".join(
                best["matched_aliases"]
            )
        )

    print(
        f"🎬 Selected Video   : "
        f"{best['title']}"
    )

    print(
        f"📺 Channel          : "
        f"{best['channel']}"
    )

    # -----------------------------------------------------
    # Build final result
    # -----------------------------------------------------

    return {

        "video_url":
            (
                "https://www.youtube.com/watch?v="
                + best["video_id"]
            ),

        "source_name":
            best["channel"],

        "youtube_title":
            best["title"],

        "youtube_video_id":
            best["video_id"],

        "published_at":
            best["published_at"],

        "thumbnail":
            best["thumbnail"],

        "relevance_score":
            best["score"]
    }


# =========================================================
# PROCESS ONE RECORD
# =========================================================

def process_record(
    video_id,
    record
):

    print()
    print("-" * 65)

    print(
        f"🎬 Processing : {video_id}"
    )

    print(
        f"🌾 Crop       : "
        f"{record.get('crop', '')}"
    )

    print(
        f"📌 Title      : "
        f"{record.get('title', '')}"
    )

    print(
        f"📂 Category   : "
        f"{record.get('category', '')}"
    )

    print(
        f"🦠 Diseases   : "
        f"{record.get('disease_ids', [])}"
    )

    result = get_best_video(
        record
    )

    if result is None:

        print()
        print(
            "⚠️ Record was NOT updated."
        )

        return False

    # -----------------------------------------------------
    # Update existing fields
    # -----------------------------------------------------

    record["video_url"] = result[
        "video_url"
    ]

    record["source_name"] = result[
        "source_name"
    ]

    # IMPORTANT
    # Do not automatically verify
    record["verified"] = False

    # -----------------------------------------------------
    # Additional useful metadata
    # -----------------------------------------------------

    record["youtube_title"] = result[
        "youtube_title"
    ]

    record["youtube_video_id"] = result[
        "youtube_video_id"
    ]

    record["published_at"] = result[
        "published_at"
    ]

    record["thumbnail"] = result[
        "thumbnail"
    ]

    record["relevance_score"] = result[
        "relevance_score"
    ]

    print()
    print("✅ DATABASE RECORD UPDATED")

    print(
        f"🔗 URL    : "
        f"{record['video_url']}"
    )

    print(
        f"📺 Source : "
        f"{record['source_name']}"
    )

    return True


# =========================================================
# MAIN DATABASE BUILDER
# =========================================================

def populate_database():

    database = load_database()

    print()
    print("=" * 65)
    print(
        "🌱 KISAN MITRA AI - "
        "VIDEO DATABASE BUILDER"
    )
    print("=" * 65)

    print()
    print(
        f"📁 Database : "
        f"{DATABASE_FILE}"
    )

    print(
        f"📊 Records  : "
        f"{len(database)}"
    )

    print()
    print(
        "⚠️ YouTube API search quota is consumed "
        "for each search."
    )

    print(
        "🎯 Relevant videos only will be saved."
    )

    updated = 0

    failed = 0

    # -----------------------------------------------------
    # Process all records
    # -----------------------------------------------------

    for index, (
        video_id,
        record
    ) in enumerate(
        database.items(),
        start=1
    ):

        print()
        print(
            f"📌 Record "
            f"{index}/{len(database)}"
        )

        success = process_record(
            video_id,
            record
        )

        if success:

            updated += 1

        else:

            failed += 1

        # -------------------------------------------------
        # Small delay between API requests
        # -------------------------------------------------

        if index < len(database):

            time.sleep(1)

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    save_database(
        database
    )

    # -----------------------------------------------------
    # Final report
    # -----------------------------------------------------

    print()
    print("=" * 65)
    print(
        "🎉 VIDEO DATABASE UPDATE COMPLETED!"
    )
    print("=" * 65)

    print()
    print(
        f"📊 Total Records : "
        f"{len(database)}"
    )

    print(
        f"✅ Updated       : "
        f"{updated}"
    )

    print(
        f"⚠️ Not Updated   : "
        f"{failed}"
    )

    print()
    print(
        f"💾 Saved At:"
    )

    print(
        DATABASE_FILE
    )

    print()
    print(
        "🔐 verified remains FALSE."
    )

    print(
        "YouTube API results are not "
        "automatically agricultural verification."
    )

    print()
    print("=" * 65)


# =========================================================
# PROGRAM ENTRY
# =========================================================

if __name__ == "__main__":

    populate_database()