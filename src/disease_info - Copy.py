"""
===========================================================
Project : Kisan Mitra AI
File    : disease_info.py
Purpose : Read disease information from diseases.json
===========================================================
"""

import json
from pathlib import Path


# =========================================================
# Database Path
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = (
    BASE_DIR
    / "disease_database"
    / "diseases.json"
)


# =========================================================
# Load Database
# =========================================================

def load_disease_database():

    if not DATABASE_FILE.exists():

        raise FileNotFoundError(
            f"Disease database not found:\n{DATABASE_FILE}"
        )

    with open(
        DATABASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        database = json.load(file)

    return database


# =========================================================
# Get Disease Information
# =========================================================

def get_disease_info(disease_id):

    database = load_disease_database()

    disease = database.get(disease_id)

    if disease is None:

        return {
            "found": False,
            "message": "Disease information not found."
        }

    return {
        "found": True,
        "data": disease
    }


# =========================================================
# Test
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print("🌱 KISAN MITRA AI - DISEASE DATABASE TEST")
    print("=" * 60)

    database = load_disease_database()

    print(
        f"\n✅ Database Loaded Successfully"
    )

    print(
        f"📊 Total Records : {len(database)}"
    )

    # Test with a known class
    test_disease = "Tomato___Late_blight"

    result = get_disease_info(
        test_disease
    )

    print(
        f"\n🔍 Testing : {test_disease}"
    )

    if result["found"]:

        disease = result["data"]

        print(
            f"🌱 Name       : {disease['name']}"
        )

        print(
            f"🌾 Crop       : {disease['crop']}"
        )

        print(
            f"🦠 Type       : {disease['type']}"
        )

        print(
            f"⚠️ Severity   : {disease['severity']}"
        )

        print(
            f"\n🔍 Symptoms:"
        )

        for symptom in disease["symptoms"]:

            print(f"   • {symptom}")

        print(
            f"\n🛠️ Treatment:"
        )

        for treatment in disease["treatment"]:

            print(f"   • {treatment}")

        print(
            f"\n🛡️ Prevention:"
        )

        for prevention in disease["prevention"]:

            print(f"   • {prevention}")

    else:

        print(
            "❌ Disease information not found."
        )

    print("\n" + "=" * 60)
    print("🎉 DATABASE TEST COMPLETED!")
    print("=" * 60)