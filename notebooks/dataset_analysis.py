import os

# Dataset Path
DATASET_PATH = "dataset/raw/PlantVillage/color"

# Check if dataset exists
if not os.path.exists(DATASET_PATH):
    print("❌ Dataset not found!")
    exit()

# Get all classes
classes = sorted(os.listdir(DATASET_PATH))

print("=" * 60)
print("🌿 Kisan Mitra AI - Dataset Report")
print("=" * 60)

print(f"\n📂 Total Classes : {len(classes)}\n")

total_images = 0

for cls in classes:
    class_path = os.path.join(DATASET_PATH, cls)

    if os.path.isdir(class_path):
        image_count = len(os.listdir(class_path))
        total_images += image_count

        print(f"{cls:<45} {image_count}")

print("\n" + "=" * 60)
print(f"🖼 Total Images : {total_images}")
print("=" * 60)