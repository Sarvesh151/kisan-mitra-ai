"""
===========================================================
Project : Kisan Mitra AI
File    : medicine_info.py
Purpose : Read verified/reference medicine-management options
          from medicine_database/medicines.json.
===========================================================
"""

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = (
    BASE_DIR
    / "medicine_database"
    / "medicines.json"
)


def load_medicine_database():

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Medicine database not found:\n{DATABASE_FILE}"
        )

    with open(
        DATABASE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_medicines_for_disease(disease_id):

    database = load_medicine_database()

    medicines = []

    for medicine_id, medicine in database.items():

        if disease_id in medicine.get(
            "target_diseases", []
        ):
            record = medicine.copy()
            record["medicine_id"] = medicine_id
            medicines.append(record)

    return medicines


def display_medicines(disease_id):

    medicines = get_medicines_for_disease(
        disease_id
    )

    print("\n" + "=" * 60)
    print("💊 MANAGEMENT / MEDICINE OPTIONS")
    print("=" * 60)

    if not medicines:
        print(
            "ℹ️ No verified/reference medicine entry "
            "is currently stored for this disease."
        )
        return

    for medicine in medicines:

        print(
            f"\n💊 {medicine['medicine_id']} - "
            f"{medicine['name']}"
        )

        print(
            f"   Category    : "
            f"{medicine['category']}"
        )

        print(
            f"   Formulation : "
            f"{medicine['formulation']}"
        )

        print(
            f"   Reference   : "
            f"{medicine['dose_reference']}"
        )

        print(
            f"   Source      : "
            f"{medicine['source']}"
        )

        print(
            f"   ⚠️ Safety   : "
            f"{medicine['safety_note']}"
        )


if __name__ == "__main__":

    print("=" * 60)
    print("🌱 KISAN MITRA AI - MEDICINE DATABASE TEST")
    print("=" * 60)

    database = load_medicine_database()

    print(
        f"\n✅ Database Loaded Successfully"
    )

    print(
        f"📊 Total Medicine Records : "
        f"{len(database)}"
    )

    test_disease = "Tomato___Late_blight"

    print(
        f"\n🔍 Testing Disease : "
        f"{test_disease}"
    )

    display_medicines(test_disease)

    print("\n" + "=" * 60)
    print("🎉 MEDICINE DATABASE TEST COMPLETED!")
    print("=" * 60)
