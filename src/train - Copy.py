"""
===========================================================
Project : Kisan Mitra AI
File    : train.py
Author  : Sarvesh Kumar
Purpose : Train EfficientNet-B0 on PlantVillage Dataset.
===========================================================
"""

import torch
import torch.nn as nn
import torch.optim as optim

from model import build_model
from data_loader import get_dataloaders
from engine import train_one_epoch, validate

from config import (
    LEARNING_RATE,
    MODEL_DIR
)


# =========================================================
# TRAINING SETTINGS
# =========================================================

# First proper training run
TRAIN_EPOCHS = 3


def main():

    # ---------------------------------------------------------
    # Device
    # ---------------------------------------------------------

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("=" * 60)
    print(f"🚀 Device : {device}")
    print("=" * 60)

    # ---------------------------------------------------------
    # Dataset
    # ---------------------------------------------------------

    train_loader, valid_loader, test_loader = get_dataloaders()

    print("\n✅ Dataset Loaded Successfully")

    # ---------------------------------------------------------
    # Model
    # ---------------------------------------------------------

    model = build_model().to(device)

    print("✅ EfficientNet-B0 Loaded Successfully")

    # ---------------------------------------------------------
    # Loss Function
    # ---------------------------------------------------------

    loss_fn = nn.CrossEntropyLoss()

    print("✅ Loss Function Ready")

    # ---------------------------------------------------------
    # Optimizer
    # ---------------------------------------------------------

    trainable_parameters = filter(
        lambda parameter: parameter.requires_grad,
        model.parameters()
    )

    optimizer = optim.Adam(
        trainable_parameters,
        lr=LEARNING_RATE
    )

    print("✅ Optimizer Ready")

    # ---------------------------------------------------------
    # Best model tracking
    # ---------------------------------------------------------

    best_val_accuracy = 0.0

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    best_model_path = (
        MODEL_DIR /
        "kisan_mitra_efficientnet_b0_best.pth"
    )

    # ---------------------------------------------------------
    # Training
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print(f"🚀 STARTING TRAINING - {TRAIN_EPOCHS} EPOCHS")
    print("=" * 60)

    for epoch in range(TRAIN_EPOCHS):

        print("\n")
        print("=" * 60)
        print(f"🌱 EPOCH {epoch + 1}/{TRAIN_EPOCHS}")
        print("=" * 60)

        # -----------------------------------------------------
        # Training
        # -----------------------------------------------------

        train_loss, train_accuracy = train_one_epoch(
            model=model,
            dataloader=train_loader,
            loss_fn=loss_fn,
            optimizer=optimizer,
            device=device
        )

        print("\n📊 Training Result")
        print(f"Train Loss     : {train_loss:.4f}")
        print(f"Train Accuracy : {train_accuracy:.2f}%")

        # -----------------------------------------------------
        # Validation
        # -----------------------------------------------------

        print("\n🔍 Starting Validation...")

        val_loss, val_accuracy = validate(
            model=model,
            dataloader=valid_loader,
            loss_fn=loss_fn,
            device=device
        )

        print("\n📊 Validation Result")
        print(f"Validation Loss     : {val_loss:.4f}")
        print(f"Validation Accuracy : {val_accuracy:.2f}%")

        # -----------------------------------------------------
        # Save best model
        # -----------------------------------------------------

        if val_accuracy > best_val_accuracy:

            best_val_accuracy = val_accuracy

            torch.save(
                model.state_dict(),
                best_model_path
            )

            print("\n💾 ⭐ BEST MODEL SAVED!")
            print(
                f"Best Validation Accuracy : "
                f"{best_val_accuracy:.2f}%"
            )

        else:

            print(
                f"\nℹ️ Best Validation Accuracy "
                f"remains : {best_val_accuracy:.2f}%"
            )

    # ---------------------------------------------------------
    # Training completed
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("🎉 TRAINING COMPLETED!")
    print("=" * 60)

    print(
        f"🏆 Best Validation Accuracy : "
        f"{best_val_accuracy:.2f}%"
    )

    print(
        f"💾 Best Model : {best_model_path}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()

    