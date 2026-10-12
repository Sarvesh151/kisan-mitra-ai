"""
===========================================================
Project : Kisan Mitra AI
File    : kisan_mitra_engine.py

Purpose :
Central application engine for Kisan Mitra AI.

It connects:
    Disease Database
    Medicine Database
    Video Database

Input:
    Disease ID

Output:
    Complete farmer guidance
===========================================================
"""

import json
from pathlib import Path


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


DISEASE_DATABASE = (
    BASE_DIR
    / "disease_database"
    / "diseases.json"
)


MEDICINE_DATABASE = (
    BASE_DIR
    / "medicine_database"
    / "medicines.json"
)


VIDEO_DATABASE = (
    BASE_DIR
    / "video_database"
    / "videos.json"
)


# =========================================================
# DATABASE LOADER
# =========================================================

def load_json_database(path):

    if not path.exists():

        raise FileNotFoundError(
            f"\nDatabase not found:\n{path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# LOAD ALL DATABASES
# =========================================================

def load_all_databases():

    diseases = load_json_database(
        DISEASE_DATABASE
    )

    medicines = load_json_database(
        MEDICINE_DATABASE
    )

    videos = load_json_database(
        VIDEO_DATABASE
    )

    return (
        diseases,
        medicines,
        videos
    )


# =========================================================
# GET DISEASE
# =========================================================

def get_disease(
    disease_id,
    diseases
):

    disease = diseases.get(
        disease_id
    )

    if disease is None:

        return None

    record = disease.copy()

    record["disease_id"] = disease_id

    return record


# =========================================================
# GET MEDICINES
# =========================================================

def get_medicines(
    disease_id,
    medicines
):

    results = []

    for medicine_id, medicine in medicines.items():

        target_diseases = medicine.get(
            "target_diseases",
            []
        )

        if disease_id in target_diseases:

            record = medicine.copy()

            record["medicine_id"] = (
                medicine_id
            )

            results.append(
                record
            )

    return results


# =========================================================
# GET VIDEOS
# =========================================================

def get_videos(
    disease_id,
    videos
):

    results = []

    for video_id, video in videos.items():

        disease_ids = video.get(
            "disease_ids",
            []
        )

        if disease_id in disease_ids:

            record = video.copy()

            record["video_id"] = (
                video_id
            )

            results.append(
                record
            )

    return results


# =========================================================
# GET COMPLETE INFORMATION
# =========================================================

def get_complete_guidance(
    disease_id
):

    (
        diseases,
        medicines,
        videos
    ) = load_all_databases()

    # -----------------------------------------------------
    # Disease
    # -----------------------------------------------------

    disease = get_disease(
        disease_id,
        diseases
    )

    if disease is None:

        return {
            "success": False,
            "error": (
                f"Disease not found: "
                f"{disease_id}"
            )
        }

    # -----------------------------------------------------
    # Medicines
    # -----------------------------------------------------

    medicine_results = get_medicines(
        disease_id,
        medicines
    )

    # -----------------------------------------------------
    # Videos
    # -----------------------------------------------------

    video_results = get_videos(
        disease_id,
        videos
    )

    # -----------------------------------------------------
    # Final response
    # -----------------------------------------------------

    return {

        "success": True,

        "disease": disease,

        "medicines": medicine_results,

        "videos": video_results
    }


# =========================================================
# DISPLAY DISEASE INFORMATION
# =========================================================

def display_disease(
    disease
):

    print()
    print("=" * 65)
    print("🌱 DISEASE INFORMATION")
    print("=" * 65)

    print(
        f"\n🦠 Disease   : "
        f"{disease.get('name', 'N/A')}"
    )

    print(
        f"🌾 Crop      : "
        f"{disease.get('crop', 'N/A')}"
    )

    print(
        f"🧬 Type      : "
        f"{disease.get('type', 'N/A')}"
    )

    print(
        f"⚠️ Severity  : "
        f"{disease.get('severity', 'N/A')}"
    )

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    description = disease.get(
        "description",
        ""
    )

    if description:

        print()
        print("📄 Description:")
        print(
            f"   {description}"
        )

    # -----------------------------------------------------
    # Symptoms
    # -----------------------------------------------------

    symptoms = disease.get(
        "symptoms",
        []
    )

    if symptoms:

        print()
        print("🔍 Symptoms:")

        for symptom in symptoms:

            print(
                f"   • {symptom}"
            )

    # -----------------------------------------------------
    # Causes
    # -----------------------------------------------------

    causes = disease.get(
        "causes",
        []
    )

    if causes:

        print()
        print("🧬 Causes:")

        for cause in causes:

            print(
                f"   • {cause}"
            )

    # -----------------------------------------------------
    # Treatment
    # -----------------------------------------------------

    treatment = disease.get(
        "treatment",
        []
    )

    if treatment:

        print()
        print("🛠️ Treatment:")

        for item in treatment:

            print(
                f"   • {item}"
            )

    # -----------------------------------------------------
    # Prevention
    # -----------------------------------------------------

    prevention = disease.get(
        "prevention",
        []
    )

    if prevention:

        print()
        print("🛡️ Prevention:")

        for item in prevention:

            print(
                f"   • {item}"
            )


# =========================================================
# DISPLAY MEDICINES
# =========================================================

def display_medicines(
    medicines
):

    print()
    print("=" * 65)
    print("💊 MEDICINE / MANAGEMENT OPTIONS")
    print("=" * 65)

    if not medicines:

        print()
        print(
            "ℹ️ No medicine record "
            "currently stored."
        )

        return

    for medicine in medicines:

        print()

        print(
            f"💊 {medicine.get('medicine_id', '')}"
            f" - "
            f"{medicine.get('name', 'N/A')}"
        )

        print(
            f"   Category    : "
            f"{medicine.get('category', 'N/A')}"
        )

        print(
            f"   Formulation : "
            f"{medicine.get('formulation', 'N/A')}"
        )

        print(
            f"   Reference   : "
            f"{medicine.get('dose_reference', 'N/A')}"
        )

        print(
            f"   Source      : "
            f"{medicine.get('source', 'N/A')}"
        )

        safety = medicine.get(
            "safety_note",
            ""
        )

        if safety:

            print(
                f"   ⚠️ Safety   : "
                f"{safety}"
            )


# =========================================================
# DISPLAY VIDEOS
# =========================================================

def display_videos(
    videos
):

    print()
    print("=" * 65)
    print("🎥 RECOMMENDED EDUCATIONAL VIDEOS")
    print("=" * 65)

    if not videos:

        print()
        print(
            "ℹ️ No video currently stored "
            "for this disease."
        )

        return

    for video in videos:

        print()

        print(
            f"🎬 {video.get('video_id', '')}"
        )

        print(
            f"   Title   : "
            f"{video.get('title', 'N/A')}"
        )

        print(
            f"   Channel : "
            f"{video.get('source_name', 'N/A')}"
        )

        print(
            f"   Language: "
            f"{video.get('language', 'N/A')}"
        )

        print(
            f"   URL     : "
            f"{video.get('video_url', 'N/A')}"
        )

        print(
            f"   Verified: "
            f"{video.get('verified', False)}"
        )


# =========================================================
# DISPLAY COMPLETE GUIDANCE
# =========================================================

def display_complete_guidance(
    disease_id
):

    result = get_complete_guidance(
        disease_id
    )

    if not result.get(
        "success",
        False
    ):

        print()
        print(
            "❌ ERROR:"
        )

        print(
            result.get(
                "error",
                "Unknown error"
            )
        )

        return

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    print()
    print("=" * 65)
    print("🌱 KISAN MITRA AI")
    print("🤖 COMPLETE FARMER GUIDANCE")
    print("=" * 65)

    # -----------------------------------------------------
    # Disease
    # -----------------------------------------------------

    display_disease(
        result["disease"]
    )

    # -----------------------------------------------------
    # Medicine
    # -----------------------------------------------------

    display_medicines(
        result["medicines"]
    )

    # -----------------------------------------------------
    # Videos
    # -----------------------------------------------------

    display_videos(
        result["videos"]
    )

    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    print()
    print("=" * 65)
    print("✅ COMPLETE GUIDANCE GENERATED")
    print("=" * 65)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("🌱 KISAN MITRA AI - CENTRAL ENGINE TEST")
    print("=" * 65)

    test_disease = (
        "Tomato___Late_blight"
    )

    print()
    print(
        f"🔍 Testing Disease:"
    )

    print(
        test_disease
    )

    display_complete_guidance(
        test_disease
    )