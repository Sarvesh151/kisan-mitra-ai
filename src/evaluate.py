"""
===========================================================
Project : Kisan Mitra AI
File    : evaluate.py
Author  : Sarvesh Kumar
Purpose : Evaluate trained EfficientNet-B0 on test dataset.
===========================================================
"""

import torch
import torch.nn as nn

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from model import build_model
from data_loader import get_dataloaders
from config import MODEL_DIR


def main():

    # =========================================================
    # Device
    # =========================================================

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 60)
    print(f"🚀 Evaluation Device : {device}")
    print("=" * 60)

    # =========================================================
    # Load Dataset
    # =========================================================

    train_loader, valid_loader, test_loader = get_dataloaders()

    print("\n✅ Test Dataset Loaded")
    print(f"🧪 Test Images : {len(test_loader.dataset)}")

    # =========================================================
    # Load Model
    # =========================================================

    model = build_model()

    model_path = (
        MODEL_DIR /
        "kisan_mitra_efficientnet_b0_best.pth"
    )

    print("\n📦 Loading Best Model...")
    print(f"Model Path : {model_path}")

    model.load_state_dict(
        torch.load(
            model_path,
            map_location=device
        )
    )

    model = model.to(device)

    model.eval()

    print("✅ Best Model Loaded Successfully")

    # =========================================================
    # Loss Function
    # =========================================================

    loss_fn = nn.CrossEntropyLoss()

    # =========================================================
    # Evaluation
    # =========================================================

    all_labels = []
    all_predictions = []

    total_loss = 0.0
    total_samples = 0

    print("\n" + "=" * 60)
    print("🧪 STARTING TEST EVALUATION")
    print("=" * 60)

    with torch.no_grad():

        for batch_idx, (images, labels) in enumerate(test_loader):

            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)

            # Loss
            loss = loss_fn(outputs, labels)

            # Predictions
            _, predictions = torch.max(
                outputs,
                dim=1
            )

            # Store results
            all_labels.extend(
                labels.cpu().numpy()
            )

            all_predictions.extend(
                predictions.cpu().numpy()
            )

            total_loss += (
                loss.item() * labels.size(0)
            )

            total_samples += labels.size(0)

            # Progress
            if (
                (batch_idx + 1) % 25 == 0
                or batch_idx == 0
                or (batch_idx + 1) == len(test_loader)
            ):

                current_accuracy = (
                    100.0 *
                    accuracy_score(
                        all_labels,
                        all_predictions
                    )
                )

                print(
                    f"Test Batch "
                    f"{batch_idx + 1}/{len(test_loader)} | "
                    f"Accuracy: "
                    f"{current_accuracy:.2f}%"
                )

    # =========================================================
    # Final Metrics
    # =========================================================

    test_loss = total_loss / total_samples

    test_accuracy = accuracy_score(
        all_labels,
        all_predictions
    )

    precision = precision_score(
        all_labels,
        all_predictions,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        all_labels,
        all_predictions,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        all_labels,
        all_predictions,
        average="weighted",
        zero_division=0
    )

    # =========================================================
    # Print Results
    # =========================================================

    print("\n" + "=" * 60)
    print("🏆 FINAL TEST RESULTS")
    print("=" * 60)

    print(f"Test Loss       : {test_loss:.4f}")
    print(f"Test Accuracy   : {test_accuracy * 100:.2f}%")
    print(f"Precision       : {precision * 100:.2f}%")
    print(f"Recall          : {recall * 100:.2f}%")
    print(f"F1 Score        : {f1 * 100:.2f}%")

    print("=" * 60)

    # =========================================================
    # Classification Report
    # =========================================================

    class_names = test_loader.dataset.dataset.classes

    print("\n📊 CLASSIFICATION REPORT")
    print("=" * 80)

    report = classification_report(
        all_labels,
        all_predictions,
        target_names=class_names,
        zero_division=0
    )

    print(report)

    # =========================================================
    # Confusion Matrix
    # =========================================================

    cm = confusion_matrix(
        all_labels,
        all_predictions
    )

    print("\n🧩 Confusion Matrix Shape:")
    print(cm.shape)

    # =========================================================
    # Save Metrics
    # =========================================================

    results_file = (
        MODEL_DIR /
        "test_results.txt"
    )

    with open(
        results_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "KISAN MITRA AI - TEST RESULTS\n"
        )

        file.write(
            "=" * 50 + "\n\n"
        )

        file.write(
            f"Test Images  : {total_samples}\n"
        )

        file.write(
            f"Test Loss    : {test_loss:.4f}\n"
        )

        file.write(
            f"Accuracy     : {test_accuracy * 100:.2f}%\n"
        )

        file.write(
            f"Precision    : {precision * 100:.2f}%\n"
        )

        file.write(
            f"Recall       : {recall * 100:.2f}%\n"
        )

        file.write(
            f"F1 Score     : {f1 * 100:.2f}%\n\n"
        )

        file.write(
            "CLASSIFICATION REPORT\n"
        )

        file.write(
            "=" * 80 + "\n"
        )

        file.write(report)

    print(
        f"\n💾 Results Saved At:\n"
        f"{results_file}"
    )

    # =========================================================
    # Save Confusion Matrix
    # =========================================================

    confusion_file = (
        MODEL_DIR /
        "confusion_matrix.txt"
    )

    with open(
        confusion_file,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "KISAN MITRA AI - CONFUSION MATRIX\n\n"
        )

        file.write(
            str(cm)
        )

    print(
        f"🧩 Confusion Matrix Saved At:\n"
        f"{confusion_file}"
    )

    print("\n" + "=" * 60)
    print("🎉 TEST EVALUATION COMPLETED!")
    print("=" * 60)


if __name__ == "__main__":
    main()