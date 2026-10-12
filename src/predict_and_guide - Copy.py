"""
===========================================================
Project : Kisan Mitra AI
File    : predict_and_guide.py

Purpose :
Connect the existing AI prediction module with the
Kisan Mitra central guidance engine.

Flow:
    Image
      ↓
    predict.py
      ↓
    Disease ID
      ↓
    kisan_mitra_engine.py
      ↓
    Disease + Medicine + Videos
===========================================================
"""

import sys
import subprocess
import re
from pathlib import Path


# =========================================================
# PROJECT PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


PREDICT_SCRIPT = BASE_DIR / "predict.py"


# =========================================================
# RUN EXISTING PREDICTION
# =========================================================

def run_prediction(image_path):

    print()
    print("=" * 65)
    print("🌱 KISAN MITRA AI - IMAGE ANALYSIS")
    print("=" * 65)

    print()
    print(f"📷 Image : {image_path}")

    if not Path(image_path).exists():

        print()
        print("❌ Image file not found:")
        print(image_path)

        return None

    if not PREDICT_SCRIPT.exists():

        print()
        print("❌ predict.py not found:")
        print(PREDICT_SCRIPT)

        return None

    print()
    print("🤖 Running AI prediction...")
    print()

    # -----------------------------------------------------
    # Run existing predict.py
    # -----------------------------------------------------

    process = subprocess.run(

        [
            sys.executable,
            str(PREDICT_SCRIPT),
            str(image_path)
        ],

        cwd=str(BASE_DIR.parent),

        capture_output=True,

        text=True,

        encoding="utf-8",

        errors="replace"
    )

    # -----------------------------------------------------
    # Show prediction output
    # -----------------------------------------------------

    if process.stdout:

        print(process.stdout)

    if process.stderr:

        print()
        print("⚠️ Prediction warnings/errors:")

        print(process.stderr)

    if process.returncode != 0:

        print()
        print(
            f"❌ Prediction process failed."
        )

        print(
            f"Exit code: {process.returncode}"
        )

        return None

    output = process.stdout

    # =====================================================
    # EXTRACT PREDICTED DISEASE
    # =====================================================

    # Expected output:
    #
    # Prediction : Tomato___Late_blight
    #

    patterns = [

        r"Prediction\s*:\s*([^\r\n]+)",

        r"Predicted Disease\s*:\s*([^\r\n]+)",

        r"Disease\s*:\s*([^\r\n]+)"
    ]

    disease_id = None

    for pattern in patterns:

        match = re.search(
            pattern,
            output,
            re.IGNORECASE
        )

        if match:

            disease_id = (
                match.group(1)
                .strip()
            )

            break

    # -----------------------------------------------------
    # Disease not found
    # -----------------------------------------------------

    if not disease_id:

        print()
        print("=" * 65)
        print("❌ DISEASE ID NOT FOUND")
        print("=" * 65)

        print()
        print(
            "The prediction script completed, "
            "but the disease ID could not be extracted."
        )

        print()
        print(
            "Please check the Prediction line "
            "printed by predict.py."
        )

        return None

    # -----------------------------------------------------
    # Remove accidental extra text
    # -----------------------------------------------------

    disease_id = disease_id.strip()

    print()
    print("=" * 65)
    print("🎯 PREDICTED DISEASE")
    print("=" * 65)

    print()
    print(
        f"🦠 Disease ID : {disease_id}"
    )

    return disease_id


# =========================================================
# LOAD CENTRAL ENGINE
# =========================================================

def load_guidance_engine():

    try:

        from kisan_mitra_engine import (
            display_complete_guidance
        )

        return display_complete_guidance

    except Exception as error:

        print()
        print(
            "❌ Could not load "
            "kisan_mitra_engine.py"
        )

        print(
            f"Error: {error}"
        )

        return None


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    # -----------------------------------------------------
    # Check image argument
    # -----------------------------------------------------

    if len(sys.argv) < 2:

        print()
        print("=" * 65)
        print("🌱 KISAN MITRA AI")
        print("=" * 65)

        print()
        print(
            "Usage:"
        )

        print(
            'python src/predict_and_guide.py "IMAGE_PATH"'
        )

        print()
        print(
            "Example:"
        )

        print(
            'python src/predict_and_guide.py '
            '"C:\\Users\\sarve\\OneDrive\\Pictures\\leaf.png"'
        )

        return

    image_path = sys.argv[1]

    # =====================================================
    # STEP 1 - AI PREDICTION
    # =====================================================

    disease_id = run_prediction(
        image_path
    )

    if disease_id is None:

        return

    # =====================================================
    # STEP 2 - LOAD GUIDANCE ENGINE
    # =====================================================

    print()
    print("=" * 65)
    print("🧠 CONNECTING TO KISAN MITRA ENGINE")
    print("=" * 65)

    display_guidance = (
        load_guidance_engine()
    )

    if display_guidance is None:

        return

    # =====================================================
    # STEP 3 - COMPLETE GUIDANCE
    # =====================================================

    print()
    print(
        f"🔗 Sending disease ID to "
        f"central engine..."
    )

    print(
        f"   {disease_id}"
    )

    # =====================================================
    # STEP 4 - DISPLAY RESULT
    # =====================================================

    display_guidance(
        disease_id
    )

    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    print()
    print("=" * 65)
    print("🎉 KISAN MITRA AI ANALYSIS COMPLETED")
    print("=" * 65)

    print()
    print("📷 Image analyzed successfully.")
    print("🦠 Disease identified.")
    print("📋 Disease information loaded.")
    print("💊 Medicine information loaded.")
    print("🎥 Educational videos loaded.")

    print()
    print("🌱 Farmer guidance is ready.")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()