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
contribution. The dataset contributor should complete the following section:

- [ ] Camera resolution, field of view, and frame rate.
- [ ] Image capture key, script, or command.
- [ ] Car route, speed range, and starting pose.
- [ ] Pedestrian route, speed range, and starting pose.
- [ ] Lighting/environment variations.
- [ ] File naming convention and metadata format.
- [x] Initial Unity environment sample in
      [`docs/samples/unity-environment-pedestrian.png`](./docs/samples/unity-environment-pedestrian.png).

## Dataset and evaluation

**To be completed by the team:**

- [ ] Dataset download location; the full dataset should not be stored in Git.
- [ ] Train/validation/test split.
- [ ] Ground-truth annotation tool and format.
- [ ] Annotation quality-control procedure.
- [ ] Evaluation dataset created from scratch.
- [ ] Baseline definition.
- [ ] Metrics, including precision, recall, F1, AP50, mAP50-95, and/or
      inference speed as appropriate.
- [ ] Model comparison or parameter-space analysis.
- [ ] Results, plots, and interpretation.

The final evaluation set must remain fixed while comparing methods. Dataset
instructions must explain how the Unity capture process connects to the
annotation and training pipeline.

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
