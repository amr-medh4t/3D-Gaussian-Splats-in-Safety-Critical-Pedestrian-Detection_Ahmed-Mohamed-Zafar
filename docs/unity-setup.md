# Unity Environment Setup

This document describes the Unity environment contribution and the handoff
point for the dataset and detection work.

## Requirements

- Unity **6000.5.6f1**
- Git LFS
- Network access for the Gaussian Splatting package declared in
  `unity/Packages/manifest.json`

## Opening the project

1. Clone the repository with Git LFS enabled.
2. Open the `unity/` folder in Unity Hub.
3. Open `Assets/Scenes/SampleScene.unity`.
4. Allow Unity to reimport the assets and regenerate the ignored `Library/`
   folder.
5. Press **Play**.

The scene was interactively verified in Unity 6000.5.6f1. The Gaussian
environment rendered, the pedestrian and vehicle were present, and no Console
errors were observed during the verification run.

## Scene contents

The main scene contains:

- Gaussian-splat buildings, streets, pavements, fences, benches, bins,
  streetlights, and other environment props.
- A main camera.
- A pedestrian with a Mixamo model and walking animation controller.
- `CrossStart` and `CrossEnd` transforms defining the pedestrian crossing.
- A car prefab using the Sketchfab model.
- URP lighting and volume settings.

The Gaussian source assets are stored in
`unity/Assets/GaussianAssets/`. Unity `.meta` files must remain alongside
their assets because they preserve Unity object references.

## Runtime behavior

### Pedestrian

`unity/Assets/HumanPath.cs` contains the `PedestrianCrosser` component. At
runtime it:

- Starts at a randomized offset near `CrossStart`.
- Moves toward `CrossEnd`.
- Uses a configurable walking speed.
- Applies a configurable speed variation.
- Stops after reaching the destination.

### Car

`unity/Assets/Azerilo/Car Model No.1201 Asset/Prefab/SimpleCarDrive.cs`
contains the `SimpleCarDrive` component. It moves the car through Unity input
axes and rotates it while moving. The exact capture route and control
procedure belong to the dataset contributor and should be documented with the
dataset protocol.

## Unity contribution boundary

This Unity contribution provides:

- The reproducible environment scene.
- Gaussian-splat asset import and placement.
- Human model and pedestrian behavior integration.
- Car model and movement integration.
- A scene ready for camera-based dataset capture.

It does not define:

- The final dataset split.
- Image capture automation.
- Ground-truth annotation.
- Detector training or evaluation.
- Baseline or model-comparison experiments.

Those items should be added by the relevant team members.

## Handoff checklist

- [x] Unity project opens with Unity 6000.5.6f1.
- [x] Gaussian environment assets import.
- [x] Main scene renders in Play mode.
- [x] Pedestrian is present and moves between the configured points.
- [x] Car is present and controllable.
- [x] No Console errors observed during interactive verification.
- [ ] Dataset capture protocol.
- [ ] Dataset and annotation instructions.
- [ ] Detection training and evaluation instructions.
