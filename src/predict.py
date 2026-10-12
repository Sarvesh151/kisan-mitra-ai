"""
===========================================================
Project : Kisan Mitra AI
File    : predict.py
Author  : Sarvesh Kumar
Purpose : Predict plant disease using EfficientNet-B0
          and display disease + medicine information.
===========================================================
"""

import sys
from pathlib import Path

import torch
from torchvision import datasets, transforms
from PIL import Image

from model import build_model
from config import DATASET_PATH, IMAGE_SIZE, MODEL_DIR
from disease_info import get_disease_info
from medicine_info import display_medicines

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


# =========================================================
# SETTINGS
# =========================================================

MODEL_NAME = "kisan_mitra_efficientnet_b0_best.pth"

CONFIDENCE_THRESHOLD = 0.60

TOP_K = 3


# =========================================================
# DEVICE
# =========================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# =========================================================
# IMAGE TRANSFORMATION
# =========================================================

transform = transforms.Compose([
    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[
            0.485,
            0.456,
            0.406
        ],
        std=[
            0.229,
            0.224,
            0.225
        ]
    )
])


# =========================================================
# LOAD CLASS NAMES
# =========================================================

def get_class_names():

    dataset = datasets.ImageFolder(
        root=DATASET_PATH
    )

    return dataset.classes


# =========================================================
# LOAD TRAINED MODEL
# =========================================================

def load_model():

    print("=" * 65)
    print("🌱 KISAN MITRA AI - MODEL LOADING")
    print("=" * 65)

    model = build_model()

    model_path = (
        MODEL_DIR / MODEL_NAME
    )

    if not model_path.exists():

        raise FileNotFoundError(
            f"\n❌ Model file not found:\n"
            f"{model_path}"
        )

    model.load_state_dict(
        torch.load(
            model_path,
            map_location=device
        )
    )

    model = model.to(device)

    model.eval()

    print(
        "✅ Model Loaded Successfully"
    )

    print(
        f"📦 Model : {model_path}"
    )

    print(
        f"🖥️ Device : {device}"
    )

    return model


# =========================================================
# DISPLAY DISEASE INFORMATION
# =========================================================

def display_disease_information(
    disease_id
):

    result = get_disease_info(
        disease_id
    )

    print("\n" + "=" * 65)
    print("📚 DISEASE INFORMATION")
    print("=" * 65)

    # -----------------------------------------------------
    # Disease Not Found
    # -----------------------------------------------------

    if not result["found"]:

        print(
            "⚠️ Disease information "
            "not found in database."
        )

        return

    disease = result["data"]

    # -----------------------------------------------------
    # Basic Information
    # -----------------------------------------------------

    print(
        f"🌱 Disease    : "
        f"{disease.get('name', 'N/A')}"
    )

    print(
        f"🌾 Crop       : "
        f"{disease.get('crop', 'N/A')}"
    )

    print(
        f"🦠 Type       : "
        f"{disease.get('type', 'N/A')}"
    )

    print(
        f"⚠️ Severity   : "
        f"{disease.get('severity', 'N/A')}"
    )

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    if disease.get("description"):

        print("\n📝 Description:")

        print(
            f"   {disease['description']}"
        )

    # -----------------------------------------------------
    # Symptoms
    # -----------------------------------------------------

    if disease.get("symptoms"):

        print("\n🔍 Symptoms:")

        for symptom in disease["symptoms"]:

            print(
                f"   • {symptom}"
            )

    # -----------------------------------------------------
    # Causes
    # -----------------------------------------------------

    if disease.get("causes"):

        print("\n🧬 Causes:")

        for cause in disease["causes"]:

            print(
                f"   • {cause}"
            )

    # -----------------------------------------------------
    # Treatment
    # -----------------------------------------------------

    if disease.get("treatment"):

        print(
            "\n🛠️ Treatment / Management:"
        )

        for treatment in disease["treatment"]:

            print(
                f"   • {treatment}"
            )

    # -----------------------------------------------------
    # Prevention
    # -----------------------------------------------------

    if disease.get("prevention"):

        print("\n🛡️ Prevention:")

        for prevention in disease["prevention"]:

            print(
                f"   • {prevention}"
            )


# =========================================================
# DISPLAY MEDICINE INFORMATION
# =========================================================

def display_medicine_information(
    disease_id
):

    print("\n")

    # medicine_info.py already handles
    # database loading and searching.

    display_medicines(
        disease_id
    )


# =========================================================
# PREDICT IMAGE
# =========================================================

def predict_image(
    image_path,
    model,
    class_names
):

    image_path = Path(
        image_path
    )

    # -----------------------------------------------------
    # Check Image
    # -----------------------------------------------------

    if not image_path.exists():

        raise FileNotFoundError(
            f"\n❌ Image not found:\n"
            f"{image_path}"
        )

    # -----------------------------------------------------
    # Open Image
    # -----------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")

    # -----------------------------------------------------
    # Transform Image
    # -----------------------------------------------------

    image_tensor = transform(
        image
    )

    image_tensor = (
        image_tensor.unsqueeze(0)
    )

    image_tensor = (
        image_tensor.to(device)
    )

    # -----------------------------------------------------
    # Prediction
    # -----------------------------------------------------

    with torch.no_grad():

        outputs = model(
            image_tensor
        )

        probabilities = (
            torch.softmax(
                outputs,
                dim=1
            )
        )

        top_probabilities, top_indices = (
            torch.topk(
                probabilities,
                TOP_K,
                dim=1
            )
        )

    # -----------------------------------------------------
    # Convert Tensor → Python
    # -----------------------------------------------------

    top_probabilities = (
        top_probabilities[0]
        .cpu()
        .numpy()
    )

    top_indices = (
        top_indices[0]
        .cpu()
        .numpy()
    )

    # -----------------------------------------------------
    # Main Prediction
    # -----------------------------------------------------

    predicted_class = (
        class_names[
            top_indices[0]
        ]
    )

    confidence = (
        top_probabilities[0]
        * 100
    )

    # =====================================================
    # PREDICTION RESULT
    # =====================================================

    print("\n" + "=" * 65)
    print("🌱 KISAN MITRA AI - PREDICTION")
    print("=" * 65)

    print(
        f"📷 Image       : "
        f"{image_path.name}"
    )

    print(
        f"🌿 Prediction  : "
        f"{predicted_class}"
    )

    print(
        f"🎯 Confidence  : "
        f"{confidence:.2f}%"
    )

    # =====================================================
    # TOP 3 PREDICTIONS
    # =====================================================

    print("\n🔝 TOP 3 PREDICTIONS")
    print("-" * 65)

    for rank in range(TOP_K):

        class_name = (
            class_names[
                top_indices[rank]
            ]
        )

        probability = (
            top_probabilities[rank]
            * 100
        )

        print(
            f"{rank + 1}. "
            f"{class_name:<45} "
            f"{probability:.2f}%"
        )

    # =====================================================
    # CONFIDENCE CHECK
    # =====================================================

    print("\n" + "-" * 65)

    if (
        top_probabilities[0]
        >= CONFIDENCE_THRESHOLD
    ):

        print(
            "✅ HIGH CONFIDENCE: "
            "Prediction is reasonably confident."
        )

        # =================================================
        # DISEASE DATABASE
        # =================================================

        display_disease_information(
            predicted_class
        )

        # =================================================
        # MEDICINE DATABASE
        # =================================================

        display_medicine_information(
            predicted_class
        )

    else:

        print(
            "⚠️ LOW CONFIDENCE"
        )

        print(
            "The AI is not sufficiently "
            "confident about this prediction."
        )

        print(
            "\n📷 Please capture a clearer "
            "leaf image."
        )

        print(
            "💡 Tips:"
        )

        print(
            "   • Use good lighting"
        )

        print(
            "   • Keep the leaf clearly visible"
        )

        print(
            "   • Avoid blurry images"
        )

        print(
            "   • Keep the camera focused "
            "on the affected leaf"
        )

    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    print("\n" + "=" * 65)

    print(
        "🌾 KISAN MITRA AI - "
        "ANALYSIS COMPLETED"
    )

    print("=" * 65)

    return {

        "prediction":
            predicted_class,

        "confidence":
            confidence,

        "top_predictions": [

            {

                "class":
                    class_names[
                        top_indices[i]
                    ],

                "confidence":
                    float(
                        top_probabilities[i]
                        * 100
                    )

            }

            for i in range(TOP_K)

        ]

    }


# =========================================================
# MAIN
# =========================================================

def main():

    # -----------------------------------------------------
    # Check Image Argument
    # -----------------------------------------------------

    if len(sys.argv) < 2:

        print("\n❌ Image path is required.")

        print(
            "\nExample:"
        )

        print(
            r'python src/predict.py "C:\Users\serve\Pictures\leaf.png"'
        )

        return

    image_path = (
        sys.argv[1]
    )

    # -----------------------------------------------------
    # Load Classes
    # -----------------------------------------------------

    class_names = (
        get_class_names()
    )

    print(
        f"\n📚 Classes Loaded : "
        f"{len(class_names)}"
    )

    # -----------------------------------------------------
    # Load Model
    # -----------------------------------------------------

    model = load_model()

    # -----------------------------------------------------
    # Predict
    # -----------------------------------------------------

    predict_image(
        image_path=image_path,
        model=model,
        class_names=class_names
    )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()