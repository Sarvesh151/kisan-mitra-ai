"""
===========================================================
Project : Kisan Mitra AI
File    : config.py
Author  : Sarvesh Kumar
Purpose : Store all project configuration settings.
===========================================================
"""

from pathlib import Path

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = PROJECT_ROOT / "dataset" / "raw" / "PlantVillage" / "color"

TRAIN_DIR = PROJECT_ROOT / "dataset" / "train"
VALID_DIR = PROJECT_ROOT / "dataset" / "valid"
TEST_DIR = PROJECT_ROOT / "dataset" / "test"

MODEL_DIR = PROJECT_ROOT / "models"

# ---------------------------------------------------------
# Image Settings
# ---------------------------------------------------------

IMAGE_SIZE = 224

# ---------------------------------------------------------
# Training Settings
# ---------------------------------------------------------

BATCH_SIZE = 32

EPOCHS = 10

LEARNING_RATE = 0.001

NUM_WORKERS = 0

# ---------------------------------------------------------
# Model Settings
# ---------------------------------------------------------

MODEL_NAME = "EfficientNet_B0"

NUM_CLASSES = 38

# ---------------------------------------------------------
# Random Seed
# ---------------------------------------------------------

RANDOM_SEED = 42