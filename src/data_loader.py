"""
===========================================================
Project : Kisan Mitra AI
File    : data_loader.py
Author  : Sarvesh Kumar
Purpose : Load and preprocess PlantVillage dataset.
===========================================================
"""

from torchvision import datasets, transforms
from torch.utils.data import DataLoader, random_split
import torch

from config import (
    DATASET_PATH,
    IMAGE_SIZE,
    BATCH_SIZE,
    RANDOM_SEED,
    NUM_WORKERS,
)


def get_dataloaders():

    # Image Transformations
    transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # Load Dataset
    dataset = datasets.ImageFolder(
        root=DATASET_PATH,
        transform=transform
    )

    # Split Dataset
    train_size = int(0.70 * len(dataset))
    valid_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - valid_size

    generator = torch.Generator().manual_seed(RANDOM_SEED)

    train_dataset, valid_dataset, test_dataset = random_split(
        dataset,
        [train_size, valid_size, test_size],
        generator=generator
    )

    # Create DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS
    )

    valid_loader = DataLoader(
        valid_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    print("=" * 60)
    print("✅ DataLoaders Ready")
    print("=" * 60)

    print(f"Train Images      : {len(train_dataset)}")
    print(f"Validation Images : {len(valid_dataset)}")
    print(f"Test Images       : {len(test_dataset)}")

    return train_loader, valid_loader, test_loader