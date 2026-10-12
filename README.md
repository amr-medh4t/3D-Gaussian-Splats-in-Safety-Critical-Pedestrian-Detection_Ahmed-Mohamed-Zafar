# 3D Gaussian Splats in Safety-Critical Pedestrian Detection

Final project for **Industrial Applications of Computer Vision**, Università degli Studi di Padova, A.A. 2025–26.

A synthetic, safety-critical driving scenario is built in Unity on top of 3D Gaussian-splat environments. A vehicle-mounted camera records pedestrians crossing the road, the frames are labeled with a model-assisted (auto-labeling) pipeline, and a single-class pedestrian detector (YOLOv8n) is trained without and with augmentation and compared against an augmented Faster R-CNN model on a fixed split.

![Unity environment with a crossing pedestrian](./docs/samples/unity-environment-pedestrian.png)

Example detection outputs (bounding boxes with confidence scores) are in [`results/ADAS_Project_drive/runs/detect/predict/`](./results/ADAS_Project_drive/runs/detect/predict/).

---

## Table of contents

1. [Team and contributions](#1-team-and-contributions)
2. [Problem definition](#2-problem-definition)
3. [Repository structure](#3-repository-structure)
4. [Setup and how to run](#4-setup-and-how-to-run)
5. [Unity environment](#5-unity-environment)
6. [Dataset](#6-dataset)
7. [Ground truth and annotation](#7-ground-truth-and-annotation)
8. [Evaluation](#8-evaluation)
9. [Third-party code, assets and licenses](#9-third-party-code-assets-and-licenses)
10. [AI and LLM usage](#10-ai-and-llm-usage)
11. [References and existing implementations](#11-references-and-existing-implementations)
12. [Known limitations](#12-known-limitations)

---

## 1. Team and contributions

Each member contributed through their own GitHub account, so the commit history documents the individual work. Where work was done jointly, it is attributed to everyone involved.

| Member | GitHub | Main area |
| --- | --- | --- |
| **Ahmed Amr** | [`amr-medh4t`](https://github.com/amr-medh4t) | Unity environment |
| **Zafar Umair** | [`wumairz`](https://github.com/wumairz) | Data collection in Unity, dataset creation |
| **Mohamed Youssef** | [`yusuf-unipd`](https://github.com/yusuf-unipd) | Auto-labeling, label verification, model training and evaluation |

### Ahmed Amr — Unity environment

- Built the Unity project (Unity **6000.5.6f1**, Universal Render Pipeline) and the main scene `Assets/Scenes/SampleScene.unity`.
- Imported the Gaussian-splat environment assets generated with PromptSplat into `Assets/GaussianAssets/`.
- Integrated the Mixamo human model and walking animation controller.
- Implemented pedestrian crossing behavior in `Assets/HumanPath.cs`: configurable `CrossStart`/`CrossEnd` endpoints, walking speed, and start/speed randomization.
- Integrated the car prefab and its manual driving script (`SimpleCarDrive.cs`).
- Organized the project for reproducible setup (package manifest, lock file, `.gitignore`, `docs/unity-setup.md`).

### Zafar Umair — Data collection and dataset creation

- **Capture pipeline:** designed and implemented `TimeRecorder.cs`, a C# recorder using `Time.unscaledDeltaTime` and `ScreenCapture` that samples continuously at 10 Hz, both while the car is driving and while it is parked.
- **Storage management:** session-timestamped output (`run_YYYYMMDD_HHMMSS`) written outside `Assets/`, so cumulative captures are not lost when Unity re-imports assets.
- **Dataset creation:** collected the full 971-frame dataset from scratch inside the Gaussian-splat environment. Capture protocols cover variable-distance straight crossings, angled and curved approaches, and sidewalk clutter occlusions (benches, poles, buildings).
- **Negative samples:** collected 282 pedestrian-free frames (empty roads, curb edges, turning maneuvers) to penalize false positives and phantom braking.
- **Dataset sorting and split (joint with Mohamed Youssef):** `training data sorter.py`, which groups images by category prefix, keeps neighboring frames of a sequence in the same split, and builds the YOLO `images/` and `labels/` layout.

### Mohamed Youssef — Labeling, training and evaluation

- **Auto-labeling:** `auto_label_pedestrians.py`, which generates preliminary single-class YOLO boxes with a pretrained Ultralytics model (see [Section 7](#7-ground-truth-and-annotation)).
- **Label verification:** carried out the two-pass verification of the generated labels described in Section 7.
- **Dataset sorting and configuration (joint with Zafar Umair):** the sorter script, plus `data.yaml` for single-class pedestrian detection.
- **Training and comparison:** trained the YOLOv8n runs (unaugmented and augmented) and the Faster R-CNN (ResNet-50 FPN) model on augmented data, in `train_and_evaluate.ipynb`, on the same split.
- **Metrics and results:** computed precision, recall, mAP50, mAP50-95 and inference time; produced the plots and run artifacts in `results/ADAS_Project_drive/runs/`.

---

## 2. Problem definition

**Goal.** Detect pedestrians crossing in front of a vehicle in a safety-critical scenario, where a missed detection can lead to a collision and a false positive can trigger unnecessary braking.

| | |
| --- | --- |
| **Input** | A single RGB frame, 1920 × 1080, from a vehicle-mounted camera in the Unity scene. |
| **Output** | Zero or more bounding boxes for the single class `pedestrian`, each with a confidence score. |
| **Out of scope** | Braking or control logic, pedestrian tracking, distance or speed estimation, multi-class detection, and real-world (non-synthetic) imagery. |

**Metrics.** Standard detection metrics, so results are comparable with other work: precision, recall, mAP50, mAP50-95, and per-image inference time.

---

## 3. Repository structure

```text
3D-Gaussian-Splats-in-Safety-Critical-Pedestrian-Detection_Ahmed-Mohamed-Zafar/
├── README.md
├── requirements.txt              Python dependencies
├── .gitignore
├── data.yaml                     YOLO dataset config (single class: pedestrian)
├── auto_label_pedestrians.py     Generates preliminary YOLO labels with a pretrained model
├── training data sorter.py       Builds the leakage-aware train/val/test split
├── train_and_evaluate.ipynb      Training, comparison and metrics
├── unity/                        Unity project (environment and capture)
│   ├── Assets/
│   │   ├── GaussianAssets/       Gaussian-splat scene assets (Git LFS)
│   │   ├── Azerilo/              Car model and SimpleCarDrive.cs
│   │   ├── Scenes/               SampleScene.unity
│   │   └── HumanPath.cs          Pedestrian crossing behavior
│   ├── Packages/                 manifest.json and packages-lock.json
│   └── ProjectSettings/
├── dataset/                      YOLO-format dataset (not versioned; see Section 6)
│   ├── images/{train,val,test}
│   └── labels/{train,val,test}
├── docs/
│   ├── unity-setup.md            Detailed Unity setup and handoff notes
│   ├── prompt-splat.md           PromptSplat documentation
│   └── samples/                  Sample images
└── results/
    └── ADAS_Project_drive/runs/  Training and validation artifacts, plots
```

`Library/`, `Logs/`, `UserSettings/` and build outputs are intentionally excluded; Unity regenerates them when the project is opened.

---

## 4. Setup and how to run

### Python environment (labeling, training and evaluation)

Training and evaluation of the YOLOv8n runs were done in Google Colab (NVIDIA T4 GPU); data preparation scripts were run locally.

| Component | Version |
| --- | --- |
| Python | 3.10 (Colab) / 3.11 (local scripts) |
| PyTorch | 2.2.0+cu121 |
| Torchvision | 0.17.0+cu121 |
| Ultralytics | 8.1.0 |
| OpenCV | opencv-python 4.9.0.80 |

```bash
pip install -r requirements.txt
```

### Pipeline

1. **Get the dataset.** Download the raw captured images from the Drive link in [Section 6](#6-dataset).
2. **Auto-label.** Generate preliminary pedestrian boxes for the pedestrian categories:
   ```bash
   python auto_label_pedestrians.py
   ```
   Set the input image folder and output label folder at the top of the script before running.
3. **Verify labels.** Apply the two-pass verification in Section 7.
4. **Build the split.** Run the sorter on the labeled images:
   ```bash
   python "training data sorter.py"
   ```
   Set the raw image/label folder and the output `dataset/` folder at the top of the script before running. The script produces the 80/10/10 split described in Section 6.
5. **Train and evaluate.** Open and run `train_and_evaluate.ipynb`. It reads `data.yaml`, trains YOLOv8n (unaugmented and augmented) and Faster R-CNN (augmented), and writes metrics and plots to `results/ADAS_Project_drive/runs/`.

### Unity project (environment and capture)

1. Install Unity **6000.5.6f1**.
2. Clone the repository with Git LFS enabled (`git lfs install` before cloning).
3. Open the `unity/` folder in Unity Hub.
4. Open `Assets/Scenes/SampleScene.unity` and let Unity reimport assets and regenerate `Library/`.
5. Press Play to check the environment, pedestrian, car and camera.

The Gaussian-splat package is declared in [`unity/Packages/manifest.json`](./unity/Packages/manifest.json) with resolved dependencies in [`packages-lock.json`](./unity/Packages/packages-lock.json). More detail is in [`docs/unity-setup.md`](./docs/unity-setup.md).

### Inputs and outputs per stage

| Stage | Input | Output |
| --- | --- | --- |
| Unity environment | Gaussian-splat assets, car and pedestrian prefabs, path parameters | A configured scene ready for vehicle-camera capture |
| Data capture | The running Unity scene | Timestamped PNG frames in `TrainingDataset/` (project root) |
| Auto-labeling | PNG frames | Preliminary YOLO `.txt` labels |
| Verification | Preliminary labels | Verified labels (empty file for negatives) |
| Sorting | Images and verified labels | `dataset/images|labels/{train,val,test}` |
| Training / evaluation | `data.yaml` and the dataset | Weights, metrics, plots, comparison table |

---

## 5. Unity environment

**Scene components**

- Gaussian-splat environment in [`unity/Assets/GaussianAssets/`](./unity/Assets/GaussianAssets), about 345 MB of binary data tracked with Git LFS.
- Pedestrian: [`HumanPath.cs`](./unity/Assets/HumanPath.cs) moves the Mixamo character between configurable `CrossStart` and `CrossEnd` points with controlled speed and start randomization.
- Car: manually driven with the Unity horizontal and vertical input axes via [`SimpleCarDrive.cs`](./unity/Assets/Azerilo/Car%20Model%20No.1201%20Asset/Prefab/SimpleCarDrive.cs), so the operator can vary route and viewpoint.

**Gaussian-splat generation.** The splats were generated locally with **PromptSplat**, a private GUI application developed with Ahmed Mounir (external collaborator, not a member of this group). It is not publicly released. PromptSplat is only a scene-generation step; it is not the detector being evaluated. See [`docs/prompt-splat.md`](./docs/prompt-splat.md).

**Capture setup**

| Parameter | Value |
| --- | --- |
| Resolution | 1920 × 1080 (Full HD, Game View buffer) |
| Field of view | 60° vertical, perspective projection |
| Camera mount | Vehicle hood, Y = 1.2 m, Z = 0.3 m |
| Capture rate | 10 Hz (one frame every 0.1 s of unscaled time) |
| Script | `TimeRecorder.cs`, attached to `Main Camera`, using `ScreenCapture.CaptureScreenshot()` |
| Output folder | `TrainingDataset/` in the project root (outside `Assets/`) |
| File naming | `run_YYYYMMDD_HHMMSS_frame_XXXXX.png` (session timestamp + 5-digit index) |

**Capture protocol**

- Stationary captures at distances from 1 m to 25 m, recording full crossing trajectories at different pixel scales.
- Straight-ahead driving runs approaching the crossing.
- Rotated camera perspectives (curved approaches, off-angle road alignments).
- Empty-road passes (full road traverse, turnarounds, curb alignments) with no pedestrian, for negative samples.

**Lighting and clutter.** Directional sunlight with Gaussian-splat ambient reflections; background clutter includes benches, trees, light poles and buildings.

---

## 6. Dataset

The evaluation dataset was **created entirely from scratch** inside the Unity Gaussian-splat environment. No pre-existing dataset is used for evaluation. COCO-pretrained weights are used only as initialization for fine-tuning.

**Download.** The full dataset is not stored in Git (images and labels are excluded via `.gitignore`):
<https://drive.google.com/drive/folders/1Ba6KrsNfvHEkJf9REvHP4OQro6xuFSt8?usp=drive_link> (anyone with the link can view and download).

**Composition (971 images)**

| Category | Images | Share | Label |
| --- | ---: | ---: | --- |
| Pedestrian crossing, straight camera | 462 | 47.6% | Pedestrian box |
| Pedestrian, rotated camera / curved approach | 152 | 15.7% | Pedestrian box |
| Distractors (sidewalk, benches, poles) | 75 | 7.7% | Empty file |
| Empty road, no pedestrian | 282 | 29.0% | Empty file |

Background categories are stored as 0-byte label files, which keeps the negative distribution without creating false annotations.

**Split.** Stratified 80/10/10 train/validation/test split, built by the sorter, identical for every model.

| Set | Images | Straight | Rotated | Distractors | Empty road |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train (80%) | 776 | ~370 | ~120 | ~61 | ~225 |
| Validation + test (20%) | 195 (≈97 val, ≈98 test) | ~92 | ~32 | ~14 | ~57 |

The sorter keeps neighboring frames of one capture sequence in the same split to avoid temporal leakage. The validation and test sets are fixed across all models.

---

## 7. Ground truth and annotation

The labels were **not drawn manually**. They were generated automatically and then verified.

- **Auto-labeling:** `auto_label_pedestrians.py` runs a pretrained Ultralytics detector (`yolov8m.pt`) on the pedestrian-category frames and writes preliminary boxes, keeping only the `pedestrian` class.
- **Format:** single-class normalized YOLO, `0 <x_center> <y_center> <width> <height>` with values in [0, 1] (`0 = pedestrian`).
- **Negative frames:** empty (0-byte) `.txt` files. Empty-road and distractor categories are never auto-labeled.
- **Annotator and verifier:** auto-labeling and verification by Mohamed Youssef.

**Verification (two passes)**

1. **Label coverage check.** Scripted checks (PowerShell) that every pedestrian image has a populated label file and every negative image has an empty one.
2. **Visual check.** Review of the generated boxes against the images to keep only valid pedestrian annotations.

Because the ground truth is model-generated, it can be biased toward what a YOLO-family detector finds easy; see [Section 12](#12-known-limitations).

---

## 8. Evaluation

**Setup.** All models are initialized from COCO-pretrained checkpoints, fine-tuned on the single-class dataset, and evaluated on the same fixed split.

| Model | Type | Initialization | Training data | Role |
| --- | --- | --- | --- | --- |
| YOLOv8n, run 1 | One-stage | `yolov8n.pt` | Unaugmented | Baseline |
| YOLOv8n, run 2 | One-stage | `yolov8n.pt` | Augmented | Improved configuration |
| Faster R-CNN, ResNet-50 FPN | Two-stage | `fasterrcnn_resnet50_fpn` (torchvision) | Augmented | Alternative approach |

Faster R-CNN is compared directly against YOLOv8n run 2, since both are trained on augmented data.

**Results**

| Model | mAP50 | mAP50-95 | Inference time (batch size 1) |
| --- | ---: | ---: | ---: |
| YOLOv8n, run 1 (unaugmented) | 0.994 (val), 0.992 (test) | not reported | not reported |
| YOLOv8n, run 2 (augmented) | 0.9918 | 0.8295 | 7.2 ms |
| Faster R-CNN (augmented) | 0.9846 | 0.8733 | 171.5 ms |

| Model | Precision | Recall |
| --- | ---: | ---: |
| YOLOv8n, run 2 (augmented) | 0.9788 | 0.9821 |
| Faster R-CNN (augmented) | ~0.942 | ~0.961 |

Inference times were measured in `train_and_evaluate.ipynb` at batch size 1. Training of the YOLOv8n runs was done on a Google Colab NVIDIA T4 GPU. The Faster R-CNN precision and recall are approximate values.

**Interpretation**

- All models reach very high mAP50 (~0.98–0.99) on this dataset, and the unaugmented and augmented YOLOv8n runs are essentially tied on mAP50.
- Faster R-CNN localizes more tightly than the augmented YOLOv8n (mAP50-95 0.8733 vs 0.8295).
- The augmented YOLOv8n is about 24× faster (7.2 ms vs 171.5 ms), which matters in a real-time safety application.
- No parameter-space analysis was carried out. The comparison covers two architectures and one augmentation change on YOLOv8n.
- Training and validation artifacts, including PR and F1 curves and comparison charts, are in [`results/ADAS_Project_drive/runs`](./results/ADAS_Project_drive/runs).

---

## 9. Third-party code, assets and licenses

| Component | Source | License / terms | Notes |
| --- | --- | --- | --- |
| Unity 6000.5.6f1 and packages | [Unity](https://unity.com/) | Unity terms; see `manifest.json` | |
| UnityGaussianSplatting | [aras-p/UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting) | MIT | Gaussian-splat rendering in Unity |
| Human model and walking animation | [Mixamo](https://www.mixamo.com/) | Adobe Mixamo terms | Redistribution confirmed by the team |
| Car model "Car for Games Unity" | [Sketchfab](https://sketchfab.com/3d-models/car-for-games-unity-4d9bbde680fe41349d7ad2b4672a720b), artist **Azerilo** | License on the Sketchfab asset page | In `Assets/Azerilo/` |
| Ultralytics YOLOv8 (incl. `yolov8n.pt`, `yolov8m.pt`) | [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics) | AGPL-3.0 | Auto-labeling, training and inference |
| PyTorch / Torchvision | [pytorch.org](https://pytorch.org/) | BSD-3-Clause | Faster R-CNN, training |
| OpenCV | [opencv.org](https://opencv.org/) | Apache-2.0 | Image processing |

---

## 10. AI and LLM usage

| Tool | Where | For what |
| --- | --- | --- |
| **PromptSplat** (private, developed with Ahmed Mounir) | Unity environment | Local generation of the Gaussian-splat scene assets from project-specific prompts |
| **Claude** | Unity code (human and car scripts) | Code assistance for the pedestrian and car behavior |
| **Claude and Gemini** | `TimeRecorder.cs` | Implementing the `Time.unscaledDeltaTime` accumulator and external path resolution relative to `Application.dataPath` |
| **Gemini and GitHub Copilot** | `training data sorter.py`, `auto_label_pedestrians.py` | Sequence-aware prefix grouping to prevent temporal leakage; auto-labeling script |
| **GitHub Copilot** | Repository | Repository organization, documentation and code review |
| **Claude** | `README.md` | Restructuring and rewording this document |

The `yolov8m.pt` detector used for auto-labeling is a pretrained model, listed in Section 9. All generated assets and code were integrated, tested and reviewed by the team, and the team can explain every design choice.

---

## 11. References and existing implementations

**Papers**

1. B. Kerbl, G. Kopanas, T. Leimkühler, G. Drettakis. *3D Gaussian Splatting for Real-Time Radiance Field Rendering.* ACM Transactions on Graphics, 2023. <https://arxiv.org/abs/2308.04079>
2. S. Ren, K. He, R. Girshick, J. Sun. *Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks.* NeurIPS 2015. <https://arxiv.org/abs/1506.01497>
3. G. Jocher, A. Chaurasia, J. Qiu. *Ultralytics YOLOv8.* 2023. <https://github.com/ultralytics/ultralytics>
4. T.-Y. Lin et al. *Microsoft COCO: Common Objects in Context.* ECCV 2014. <https://arxiv.org/abs/1405.0312>

**Existing implementations and models**

- [aras-p/UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting)
- Ultralytics `yolov8n.pt` and `yolov8m.pt` (COCO-pretrained)
- Torchvision `fasterrcnn_resnet50_fpn` (COCO-pretrained)

**Positioning of this work**

| | |
| --- | --- |
| **Reused** | The Unity Gaussian-splat renderer, COCO-pretrained YOLOv8 and Faster R-CNN weights, the Ultralytics and torchvision training APIs, `yolov8m.pt` for auto-labeling. |
| **Adapted** | Detectors fine-tuned to a single `pedestrian` class; YOLOv8n trained without and with augmentation; Faster R-CNN trained with augmentation. |
| **Created by the team** | The Unity scene, pedestrian and car behavior, the capture recorder, the full 971-image dataset, the auto-labeling and verification pipeline, the leakage-aware sorter, and the evaluation and comparison. |

---

## 12. Known limitations

- **Labels are model-generated.** Ground truth comes from an auto-labeling pass with a YOLO-family model, followed by verification, not from independent manual annotation. Evaluating YOLO detectors against YOLO-made labels may overstate their accuracy, and may partly explain the near-saturated mAP50 (~0.99).
- All data is synthetic and comes from a single Unity scene with directional sunlight, so lighting, weather and appearance variety are limited. There is no validation on real-world footage.
- Single class (`pedestrian`) and a single pedestrian model, so diversity of appearance is low.
- Frames are sampled at 10 Hz, so frames within a sequence are highly correlated. Grouping them in one split reduces leakage, but the near-saturated scores suggest the task is relatively easy in this setting.
- The comparison covers two architectures and one augmentation change on YOLOv8n. No parameter-space or ablation study was done, and no traditional (non-deep-learning) method is included.
- The work covers detection only; no braking logic, tracking or distance estimation is implemented.
- The Gaussian-splat package is fetched from an external Git repository, and the large splat assets need Git LFS or external storage.
- PromptSplat is not publicly released, so the splat assets cannot be regenerated from this repository alone.
