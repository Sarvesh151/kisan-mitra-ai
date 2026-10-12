"""
===========================================================
Project : Kisan Mitra AI
File    : create_disease_database.py
Purpose : Create disease database structure automatically
          from PlantVillage dataset classes.
===========================================================
"""

import json
from pathlib import Path

from torchvision import datasets

from config import DATASET_PATH


# =========================================================
# Database Path
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "disease_database"

DATABASE_FILE = DATABASE_DIR / "diseases.json"


# =========================================================
# Create Database
# =========================================================

def create_database():

    print("=" * 60)
    print("🌱 KISAN MITRA AI - DISEASE DATABASE")
    print("=" * 60)

    # -----------------------------------------------------
    # Load dataset classes
    # -----------------------------------------------------

    print("\n📚 Reading disease classes from dataset...")

    dataset = datasets.ImageFolder(
        root=DATASET_PATH
    )

    class_names = dataset.classes

    print(
        f"✅ {len(class_names)} classes found."
    )

    # -----------------------------------------------------
    # Create database directory
    # -----------------------------------------------------

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Create disease records
    # -----------------------------------------------------

    disease_database = {}

    for class_name in class_names:

        # Convert dataset label into readable name
        readable_name = (
            class_name
            .replace("___", " - ")
            .replace("_", " ")
        )

        disease_database[class_name] = {

            "name": readable_name,

            "crop": "",

            "type": "",

            "severity": "",

            "description": "",

            "symptoms": [],

            "causes": [],

            "treatment": [],

            "prevention": [],

            "medicine_ids": [],

            "video_ids": []

        }

    # -----------------------------------------------------
    # Save JSON
    # -----------------------------------------------------

    with open(
        DATABASE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            disease_database,
            file,
            indent=4,
            ensure_ascii=False
        )

    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("🎉 DATABASE CREATED SUCCESSFULLY!")
    print("=" * 60)

    print(
        f"\n📊 Total Classes : {len(class_names)}"
    )

    print(
        f"📁 Database File : {DATABASE_FILE}"
    )

    print("\n🦠 Disease Classes:")

    for index, class_name in enumerate(
        class_names,
        start=1
    ):

        print(
            f"{index:02d}. {class_name}"
        )

    print("\n" + "=" * 60)


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":
    create_database()