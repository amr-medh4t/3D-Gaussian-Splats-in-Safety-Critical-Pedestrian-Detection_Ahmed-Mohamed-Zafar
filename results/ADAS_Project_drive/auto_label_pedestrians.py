import argparse
import os
from ultralytics import YOLO

parser = argparse.ArgumentParser(description="Generate YOLO pedestrian labels.")
parser.add_argument("--dataset", default=r"C:\Users\ye293\Downloads\computer vision\TrainingDataset\TrainingDataset\dataset")
parser.add_argument("--model", default="yolov8m.pt")
parser.add_argument("--confidence", type=float, default=0.30)
args = parser.parse_args()

labeler = YOLO(args.model)

DATASET_PATH = args.dataset

splits = ['train', 'val', 'test']

for split in splits:
    img_dir = os.path.join(DATASET_PATH, 'images', split)
    lbl_dir = os.path.join(DATASET_PATH, 'labels', split)

    for img_name in sorted(os.listdir(img_dir)):
        if not (img_name.startswith('pedestrian') or img_name.startswith('pedestrian_rotated')):
            continue

        img_path = os.path.join(img_dir, img_name)
        base_name = os.path.splitext(img_name)[0]
        txt_path = os.path.join(lbl_dir, f"{base_name}.txt")

        results = labeler(img_path, verbose=False)[0]
        lines = []

        for box in results.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())

            if cls_id == 0 and conf > args.confidence:
                x, y, w, h = box.xywhn[0].tolist()
                lines.append(f"0 {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

        # Always write the file so a no-detection result is explicit.
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

print("Auto-labeling complete! Bounding boxes generated.")
