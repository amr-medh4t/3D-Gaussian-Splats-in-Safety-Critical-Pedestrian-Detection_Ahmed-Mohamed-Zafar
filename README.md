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
The final report must describe the generation prompt/configuration and cite the
PromptSplat implementation used.

## Input and output of the Unity stage

**Inputs**

- Unity scene and imported Gaussian-splat assets.
- Car and pedestrian prefabs.
- Configured movement paths and scene parameters.

**Outputs**

- RGB images captured from the vehicle camera.
- Scene/configuration metadata needed to reproduce each capture.
- A dataset to be annotated for pedestrian detection.

### Capture protocol

**To be completed by the Unity contributor before final submission:**

- [ ] Camera resolution, field of view, and frame rate.
- [ ] Image capture key, script, or command.
- [ ] Car route, speed range, and starting pose.
- [ ] Pedestrian route, speed range, and starting pose.
- [ ] Lighting/environment variations.
- [ ] File naming convention and metadata format.
- [ ] Example captured frames in `docs/samples/`.

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
  documentation in [`PROJECT_IMPLEMENTATION.md`](./PROJECT_IMPLEMENTATION.md).
- The Azerilo car asset and the human model/animation asset included under
  `unity/Assets/`.

**Before public release, the team must verify the redistribution license for
each downloaded model, texture, animation, and package.** If an asset license
does not permit redistribution, remove the binary from the repository and
document how evaluators can obtain it legally.

## AI and LLM usage

**To be completed and reviewed by the team:** document every AI/LLM tool used,
where it was used, and what was accepted or corrected by a human. This should
include PromptSplat generation, code assistance, model training assistance,
and documentation assistance where applicable.

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
- Initial Unity project organization for reproducible scene capture.

**To be completed by the team:** add each member’s name, GitHub account,
technical contribution, and the commits or subsystem associated with that
contribution.

## Known limitations of this stage

- The full capture protocol is not yet documented here.
- Dataset annotations and detector results are not part of this Unity-only
  stage.
- The Gaussian-splat package is retrieved from an external Git repository.
- Large binary assets require Git LFS or documented external storage.
- The public redistribution status of third-party models and textures still
  needs to be verified.
