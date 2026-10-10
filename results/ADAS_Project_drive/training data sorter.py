import argparse
import os
import random
import re
import shutil
from collections import defaultdict

parser = argparse.ArgumentParser(description="Create a leakage-aware YOLO dataset split.")
parser.add_argument("--source", default=None, help="Folder containing the source images.")
parser.add_argument("--dataset", default="./dataset", help="Output YOLO dataset folder.")
parser.add_argument("--group-size", type=int, default=10, help="Consecutive frames kept in one split group.")
parser.add_argument("--clean", action="store_true", help="Remove existing output images and labels first.")
args = parser.parse_args()

if args.group_size < 1:
    parser.error("--group-size must be at least 1")

SOURCE_DIR = args.source or ("./raw_images" if os.path.isdir("./raw_images") else ".")
DATASET_DIR = args.dataset

SPLITS = {"train": 0.80, "val": 0.10, "test": 0.10}
CATEGORIES = ["pedestrian_rotated", "car_near_sidewalk", "Distractors", "pedestrian", "empty"]

if args.clean and os.path.isdir(DATASET_DIR):
    shutil.rmtree(DATASET_DIR)

# Build YOLO directory structure
for split in SPLITS.keys():
    os.makedirs(os.path.join(DATASET_DIR, "images", split), exist_ok=True)
    os.makedirs(os.path.join(DATASET_DIR, "labels", split), exist_ok=True)

# Group images by category prefix
grouped_images = defaultdict(list)
all_files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for file in all_files:
    for cat in CATEGORIES:
        if file.startswith(cat):
            grouped_images[cat].append(file)
            break

# Keep nearby frames together so random splitting cannot place adjacent frames
# from one capture sequence in different splits.
random.seed(42)
for cat, files in grouped_images.items():
    def natural_key(filename):
        return [int(part) if part.isdigit() else part.lower()
                for part in re.split(r"(\d+)", filename)]

    files.sort(key=natural_key)
    groups = [files[index:index + args.group_size]
              for index in range(0, len(files), args.group_size)]
    random.shuffle(groups)
    n_groups = len(groups)
    n_train = max(1, int(n_groups * SPLITS["train"])) if n_groups else 0
    n_val = max(1, int(n_groups * SPLITS["val"])) if n_groups > 1 else 0
    if n_train + n_val >= n_groups and n_groups > 1:
        n_train = max(1, n_groups - 2)
        n_val = 1

    split_bins = {
        "train": [file for group in groups[:n_train] for file in group],
        "val": [file for group in groups[n_train:n_train + n_val] for file in group],
        "test": [file for group in groups[n_train + n_val:] for file in group],
    }
    
    for split_name, assigned_files in split_bins.items():
        for filename in assigned_files:
            src_img = os.path.join(SOURCE_DIR, filename)
            dst_img = os.path.join(DATASET_DIR, "images", split_name, filename)
            shutil.copy2(src_img, dst_img)
            
            # Empty files are valid labels for known background images.
            base_name = os.path.splitext(filename)[0]
            label_path = os.path.join(DATASET_DIR, "labels", split_name, f"{base_name}.txt")
            if cat in ["empty", "Distractors", "car_near_sidewalk"]:
                open(label_path, "w", encoding="utf-8").close()

print(f"Grouped splitting complete: source={SOURCE_DIR}, output={DATASET_DIR}")
for split_name in SPLITS:
    image_count = len(os.listdir(os.path.join(DATASET_DIR, "images", split_name)))
    print(f"{split_name}: {image_count} images")