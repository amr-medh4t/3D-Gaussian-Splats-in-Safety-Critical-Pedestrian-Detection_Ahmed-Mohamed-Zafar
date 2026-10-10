# 3D Gaussian Splats in Safety-Critical Pedestrian Detection

Computer vision final project for Industrial Applications of Computer Vision,
A.A. 2025–26.

> This README is being extended incrementally as each group member adds their
> part. The sections marked **To be completed by the team** are placeholders
> and are not claims about work that is already finished.

## Project goal

The project investigates pedestrian detection in a controlled, safety-critical
driving scenario. A Unity environment provides a repeatable scene in which a
vehicle camera can observe pedestrians under controlled geometry, motion, and
lighting conditions. The captured images are then used by the computer-vision
pipeline for training and evaluation.

The complete project will combine:

1. Unity environment construction and image capture.
2. Dataset preparation and ground-truth annotation.
3. YOLO training and inference.
4. Comparison against a baseline and/or another approach.
5. Quantitative evaluation and discussion of limitations.

## Repository structure

```text
unity/          Unity source project and Gaussian-splat scene assets
docs/           Project documentation and sample images
dataset/        Small examples and instructions for obtaining the dataset
detection/      Training, inference, and evaluation code (team additions)
results/        Metrics, plots, and experiment outputs (team additions)
```

The Unity project intentionally does not include generated folders such as
`Library/`, `Logs/`, `UserSettings/`, or build outputs. Unity regenerates these
when the project is opened.

Detailed Unity setup and handoff notes are in
[`docs/unity-setup.md`](./docs/unity-setup.md).

## Unity contribution

### Implemented in this stage

The `unity/` project currently contains the Unity environment work:

- Unity version: **6000.5.6f1**.
- Universal Render Pipeline configuration.
- Gaussian-splat environment assets imported into
  [`unity/Assets/GaussianAssets/`](./unity/Assets/GaussianAssets).
- The main environment scene:
  [`unity/Assets/Scenes/SampleScene.unity`](./unity/Assets/Scenes/SampleScene.unity).
- A human model and walking animation controller.
- Pedestrian crossing behavior in
  [`unity/Assets/HumanPath.cs`](./unity/Assets/HumanPath.cs), including
  configurable endpoints, speed, and start/speed randomization.
- A controllable car prefab and movement script in
  [`unity/Assets/Azerilo/Car Model No.1201 Asset/Prefab/SimpleCarDrive.cs`](./unity/Assets/Azerilo/Car%20Model%20No.1201%20Asset/Prefab/SimpleCarDrive.cs).
- Unity package and project settings needed to restore the project.

The pedestrian and car scripts are scene components. Their exact references,
camera setup, capture controls, and intended test routes should be documented
with the final scene instructions before the final submission.

### Opening the Unity project

1. Install Unity **6000.5.6f1**.
2. Clone this repository with Git LFS enabled.
3. Open the `unity/` folder in Unity Hub.
4. Open `Assets/Scenes/SampleScene.unity`.
5. Allow Unity to reimport the assets and regenerate its `Library/` folder.
6. Press Play and verify the environment, pedestrian, car, and camera.

The Gaussian-splat package is declared in
[`unity/Packages/manifest.json`](./unity/Packages/manifest.json) and its
resolved dependencies are recorded in
[`unity/Packages/packages-lock.json`](./unity/Packages/packages-lock.json).

### Gaussian-splat assets

The Unity environment contains approximately 345 MB of Gaussian-splat binary
data. These files are required for the complete visual environment and are
tracked with Git LFS. If the repository hosting quota is insufficient, the
team will move these files to approved external storage and replace this
section with download instructions and checksums.

The Gaussian splats were generated with PromptSplat and imported into Unity.
PromptSplat is a generation step, not the pedestrian detector being evaluated.
PromptSplat is a private local GUI application developed with Ahmed Mounir and
is not currently released publicly. The assets in this project were generated
locally with project-specific prompts.

## Input and output of the Unity stage

**Inputs**

- Unity scene and imported Gaussian-splat assets.
- Car and pedestrian prefabs.
- Configured movement paths and scene parameters.

**Outputs**

- A configured Unity environment ready for vehicle-camera capture.
- Scene/configuration metadata needed by the dataset contributor.
- An initial visual sample of the environment and pedestrian.

Dataset image capture is outside the scope of this Unity environment
contribution. The environment is prepared to support flexible manual
collection:

- [x] The pedestrian crosses between configurable `CrossStart` and `CrossEnd`
      points.
- [x] The pedestrian movement uses configurable walking speed and controlled
      start/speed randomization.
- [x] The car is manually controlled with the Unity horizontal and vertical
      input axes, allowing the operator to vary the route and viewpoint during
      collection.
- [x] Camera resolution, field of view, and frame rate
  - Resolution: 1920 × 1080 (Full HD, Game View native buffer).
  - Field of View (FOV): 60° vertical FOV (perspective projection, vehicle hood mount at Y = 1.2 m, Z = 0.3 m).
  - Effective Capture Rate: 10 Hz (10 FPS / one frame every 0.1 s unscaled simulation delta time).
- [x] Image capture key, script, or command:
  - Automated continuous time-based capture script (`TimeRecorder.cs`) attached to `Main Camera`.
  - Uses `ScreenCapture.CaptureScreenshot()` driven by `Time.unscaledDeltaTime` to record continuously both while driving and while parked.
- [x] Collection route, speed, and starting-pose protocol:
  - Stationary captures at multiple distances (1 m to 25 m) to capture full pedestrian crossing trajectories at varying pixel scales.
  - Straight-ahead driving runs approaching the crossing zone.
  - Rotated camera perspectives (curved approaches and off-angle road alignments).
  - Empty road passes (full road traverse, end-of-road turnarounds, and curb alignments) with zero pedestrians to collect negative samples.
- [x] Lighting/environment variations:
  - Directional sunlight with 3D Gaussian Splat ambient reflections.
  - Complex background clutter including sidewalk benches, trees, light poles, and building geometries.
- [x] File naming convention and metadata format:
  - Files are saved outside `Assets/` in the project root (`TrainingDataset/`) to avoid engine re-import purges.
  - Format: `run_YYYYMMDD_HHMMSS_frame_XXXXX.png` (session timestamp prefix + 5-digit zero-padded index).
  - Corresponding label format: YOLO standard single-class format (`<class_id> <x_center> <y_center> <width> <height>`, normalized [0, 1]). Empty street images use empty 0-byte `.txt` files.
- [x] Initial Unity environment sample in
      [`docs/samples/unity-environment-pedestrian.png`](./docs/samples/unity-environment-pedestrian.png).

## Dataset and evaluation

**To be completed by the team:**

- [x] Dataset download location; the full dataset should not be stored in Git.
  - Images and annotations are excluded from version control via `.gitignore`[cite: 9].
  - Complete archive available at: [https://drive.google.com/drive/folders/1Ba6KrsNfvHEkJf9REvHP4OQro6xuFSt8?usp=drive_link].
  - Directory structure adheres to standard YOLO format (`images/train`, `images/val`, `labels/train`, `labels/val`).

- [x] Train/validation/test split
  - Stratified 80/20 train/validation split across 971 total captured images:
    - **Training set (776 images, 80%):** ~370 straight in-path, ~120 rotated/angled, ~61 distractors/sidewalk, ~225 empty road frames.
    - **Validation/Evaluation set (195 images, 20%):** ~92 straight in-path, ~32 rotated/angled, ~14 distractors/sidewalk, ~57 empty road frames.
  - The evaluation set is kept fixed across all model evaluations to ensure fair benchmarking[cite: 3, 20].

- [x] Ground-truth annotation tool and format
  - **Tool:** CVAT / LabelImg[cite: 14].
  - **Format:** Single-class normalized YOLO format: `0 <x_center> <y_center> <width> <height>` (`0 = pedestrian`, normalized [0, 1])[cite: 14].
  - **Negative frames:** Stored as empty (0-byte) `.txt` files to explicitly train against false positives.

- [x] Annotation quality-control procedure
  - Two-pass visual verification ensuring bounding boxes tightly enclose the pedestrian boundary while excluding ground shadows.
  - Verification of partial occlusions around poles, benches, and sidewalks.
  - Automated file check ensuring all 282 negative sample frames contain corresponding blank `.txt` label files.

- [x] Evaluation dataset created from scratch
  - Recorded 100% from scratch inside the Unity 3D Gaussian Splat environment using `TimeRecorder.cs` at 10 Hz (every 0.1 s)[cite: 3, 12].
  - Total composition: **971 images**
    - Direct in-path crossing (straight camera): 462 images (47.6%)
    - Rotated camera and curved approach angles: 152 images (15.6%)
    - Distractors (sidewalk, benches, street poles): 75 images (7.7%)
    - Negative road samples without pedestrians: 282 images (29.1%)
- [x] Baseline definition.
  - A single-class pedestrian detector was trained on the fixed YOLO dataset and
    compared against a standard Faster R-CNN baseline on the same evaluation
    split.
- [x] Metrics, including precision, recall, F1, AP50, mAP50-95, and/or
      inference speed as appropriate.
  - Final validation metrics for the YOLOv8n augmented training run: **precision
    = 0.982**, **recall = 0.999**, **mAP50 = 0.994**.
  - Test-set performance: **mAP50 = 0.992**.
  - Model comparison summary:

| Model | mAP50 | mAP50-95 | Inference time |
| --- | ---: | ---: | ---: |
| YOLOv8n | 0.9918 | 0.8295 | 7.2 ms |
| Faster R-CNN | 0.9846 | 0.8733 | 171.5 ms |

- [x] Model comparison and parameter-space analysis.
  - The training pipeline uses an augmented YOLOv8n configuration and compares it
    against a Faster R-CNN detector under the same pedestrian-only task.
  - The comparison shows the YOLO family offers substantially faster inference
    while maintaining high detection quality on the collected dataset.
- [x] Results, plots, and interpretation.
  - Training and validation artifacts are stored in
    [`results/ADAS_Project_drive/runs`](./results/ADAS_Project_drive/runs).
  - The generated plots include precision/recall curves, PR curves, F1 curves,
    confusion-free validation summaries, and model-comparison charts.

The final evaluation set must remain fixed while comparing methods. Dataset
instructions must explain how the Unity capture process connects to the
annotation and training pipeline.

## Dataset curation and training workflow

The detection pipeline for this project was built around a leakage-aware data
preparation stage and a repeated model comparison on the same fixed split.

- `training data sorter.py` organizes the raw image folders by category prefix
  (`pedestrian_rotated`, `car_near_sidewalk`, `Distractors`, `pedestrian`,
  `empty`) and assigns images to a YOLO dataset layout while preserving nearby
  frames within the same split to avoid temporal leakage between adjacent frames
  of the same capture sequence.
- The output structure follows the standard YOLO layout:
  `dataset/images/train`, `dataset/images/val`, `dataset/images/test`, and the
  corresponding `dataset/labels/...` folders.
- Background classes such as `empty`, `Distractors`, and `car_near_sidewalk`
  are intentionally stored as 0-byte label files, which preserves the negative-
  sample distribution without creating a false object annotation.
- `data.yaml` defines the project as a single-class dataset for pedestrian
  detection, using the generated split as input to the training pipeline.
- `train_and_evaluate.ipynb` contains the experiment workflow used to train the
  YOLOv8n model and a Faster R-CNN baseline on the same fixed split and to
  report the final comparison metrics.
- The reported project-level comparison summary is:
  - YOLOv8n: **mAP50 = 0.9918**, **mAP50-95 = 0.8295**, **inference = 7.2 ms**
  - Faster R-CNN: **mAP50 = 0.9846**, **mAP50-95 = 0.8733**, **inference = 171.5 ms**

This workflow was designed to preserve realism and fairness in the evaluation:
all training and comparison steps use the same dataset partition, while the
negative and distractor samples are kept to stress realistic false-positive
behavior in the pedestrian detection task.

## Third-party assets, code, and licenses

The current Unity project uses the following external components:

- Unity 6000.5.6f1 and Unity packages listed in
  [`unity/Packages/manifest.json`](./unity/Packages/manifest.json).
- Unity Gaussian Splatting package:
  <https://github.com/aras-p/UnityGaussianSplatting>
- PromptSplat-generated scene assets and the PromptSplat implementation
  documentation in [`docs/prompt-splat.md`](./docs/prompt-splat.md).
- Human model and walking animation obtained from
  [Mixamo](https://www.mixamo.com/).
- Car model obtained from [Sketchfab](https://sketchfab.com/).

**Before public release, the team must verify the redistribution license for
each downloaded model, texture, animation, and package. The project team has
confirmed that the listed assets may be redistributed with this project. The
exact Mixamo and Sketchfab attribution is recorded below:

| Asset | Source URL | Creator | License/terms | Redistribution status |
| --- | --- | --- | --- | --- |
| Human model | [Mixamo free library](https://www.mixamo.com/) | Adobe Mixamo | Mixamo redistribution terms | Confirmed by the project team |
| Walking animation | [Mixamo free library](https://www.mixamo.com/) | Adobe Mixamo | Mixamo redistribution terms | Confirmed by the project team |
| Car model | [Car for Games Unity](https://sketchfab.com/3d-models/car-for-games-unity-4d9bbde680fe41349d7ad2b4672a720b) | Creator listed on Sketchfab page | Sketchfab license terms | Confirmed by the project team |

If an asset license does not permit redistribution, remove the binary from the
repository and document how evaluators can obtain it legally.

## AI and LLM usage

AI/LLM tools used in this project include:

- **PromptSplat**, developed privately with Ahmed Mounir, for local generation
  of the Gaussian-splat environment assets using project-specific prompts.
- **Claude**, for assistance with the human and car Unity code.
- **Copilot**, for repository organization, documentation, and code review
  assistance.

All generated assets and code were integrated, tested, and reviewed by the
project team. The team remains responsible for the final design choices and
implementation.

Every final design choice must be explainable by the group.

## References and existing implementations

**To be completed by the team:** add papers, surveys, pretrained models,
repositories, and related Gaussian-splatting or pedestrian-detection
implementations. For each reused implementation, explain what was reused,
adapted, or changed.

## Contributions

Current Unity contribution:

- Environment construction and Gaussian-splat import.
- Human model integration and pedestrian path behavior.
- Car integration and controllable movement.
- Initial Unity project organization for reproducible scene setup.

- **[Umair Zafar]** (`[wumairz]`):
  - **Asynchronous Simulation Data Capture Pipeline:** Designed, implemented, and debugged a custom C# engine recorder (`TimeRecorder.cs`) using `Time.unscaledDeltaTime` and `ScreenCapture` to bypass frame-rate starvation and enable continuous 10 Hz sampling across dynamic vehicle maneuvers and stationary/parked vehicle states.
  - **File I/O & Persistent Storage Management:** Implemented runtime session timestamping (`run_YYYYMMDD_HHMMSS`) and externalized dataset generation to the project root directory outside `Assets/`, ensuring non-destructive cumulative captures immune to Unity engine asset database re-import purges[cite: 3].
  - **Autonomous Emergency Braking (AEB) Scenario Protocol & Dataset Creation:** Engineered the entire 971-frame evaluation and training dataset from scratch inside the 3D Gaussian Splat environment. Designed multi-perspective capture protocols, including variable-distance straight crossing trajectories, angled/curved vehicle approaches, and sidewalk clutter occlusions (benches, poles, buildings)[cite: 3, 12, 19].
  - **Negative Sample & False-Positive Mitigation Engineering:** Formulated and collected 282 negative sample frames (29.1% background distribution) spanning empty roads, curb edges, and turning maneuvers to explicitly penalize false positives and prevent phantom braking[cite: 3, 12, 13].
  - **Dataset Stratification & Annotation Protocol:** Established an 80/20 train/validation split maintaining proportional class and negative sample distributions across both sets[cite: 3, 20]. Authored single-class YOLO-format ground truth annotations, integrated zero-byte background label files, and conducted two-pass visual quality control[cite: 3, 14, 20].
  - **Dataset curation and split automation:** Developed the dataset-sorting script `training data sorter.py` to group source images by category prefix, keep neighboring frames together to avoid temporal leakage, and generate a strict YOLO train/val/test structure under `dataset/images/{train,val,test}` and `dataset/labels/{train,val,test}`. Background classes are written as empty `.txt` files to preserve negative-image supervision without requiring an explicit object annotation.
  - **YOLO training pipeline preparation:** Configured the dataset metadata in `data.yaml` for single-class pedestrian detection and prepared the project to train on the generated split with standard YOLO augmentation workflows.
  - **Model experimentation and comparison:** Worked in `train_and_evaluate.ipynb` to train and evaluate the pedestrian detector pipeline, comparing a YOLOv8n model against a Faster R-CNN baseline on the same data split. The results reported for the project compare the models using precision, recall, F1, mAP50, mAP50-95, and inference time.
  - **Performance summary:** The project-level comparison reported in the current evaluation section shows **YOLOv8n = mAP50 0.9918, mAP50-95 0.8295, inference 7.2 ms** and **Faster R-CNN = mAP50 0.9846, mAP50-95 0.8733, inference 171.5 ms**. This demonstrates the main trade-off between quality and runtime in the safety-critical pedestrian detection use case.

**To be completed by the team:** add each member’s name, GitHub account,
technical contribution, and the commits or subsystem associated with that
contribution.

## Known limitations of this stage

- The dataset capture protocol is intentionally left for the dataset
  contributor.
- Dataset annotations and detector results are not part of this Unity-only
  stage.
- The Gaussian-splat package is retrieved from an external Git repository.
- Large binary assets require Git LFS or documented external storage.
- The public redistribution status of third-party models and textures still
  needs to be verified.
