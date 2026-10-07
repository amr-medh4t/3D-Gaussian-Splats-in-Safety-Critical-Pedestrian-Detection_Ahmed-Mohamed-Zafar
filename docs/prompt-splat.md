# PromptSplat: Project Architecture and Detailed Implementation

> This document describes the PromptSplat pipeline used to generate the
> environment assets imported by the Unity project. This repository contains
> the generated Unity assets and integration, not the complete standalone
> PromptSplat source pipeline.

PromptSplat is a private, locally run GUI application developed with Ahmed
Mounir. It is not currently released as a public repository. The environments
in this project were generated locally using prompts authored for this project.

## 1. Project summary

PromptSplat is a prompt-to-3D environment pipeline. It accepts a natural-language description such as “a three-floor brick house” or “a four-lane street with buildings,” turns that description into a constrained scene plan, builds the scene in Blender, and exports two synchronized assets:

- `scene_splat.ply`: the visible scene as a 3D Gaussian Splatting-compatible point cloud.
- `collider.glb`: a simplified triangle mesh used for physics and collision in Unity.

The same run also produces preview screenshots, an interactive browser preview, and a manifest describing the generated files.

The project is designed to make inexpensive, repeatable 3D environment generation practical. It does not train a Gaussian-splat model from photographs. Instead, it procedurally creates a conventional mesh, bakes its appearance, samples the mesh surface, and encodes every sample as an oriented Gaussian. This makes generation much faster and more deterministic than an image-based reconstruction pipeline.

## 2. Why the project exists

Most text-to-3D systems optimize for a visually interesting result but do not also provide a clean collision representation suitable for a game engine. PromptSplat produces the visual and physical representations together, from the same source geometry, so they remain spatially aligned.

The project also addresses a recurring weakness of LLM-generated 3D scenes: language models are good at interpreting intent, but unreliable at low-level spatial arithmetic. Asking a model to independently place every wall, window, roof panel, road, and prop frequently produces disconnected walls, floating objects, overlapping roads, duplicate roofs, or unrealistic scale.

PromptSplat therefore separates responsibilities:

1. AI interprets the user’s intent and selects high-level bounded parameters.
2. JSON Schema validation and semantic checks reject or repair invalid parameters.
3. Deterministic Blender generators calculate all detailed coordinates and geometry.
4. Visual feedback agents inspect rendered evidence and guide subsequent corrections.

This division keeps the system flexible at the semantic level while making the geometric core predictable and testable.

## 3. End-to-end architecture

```text
User prompt or Quick Build controls
                |
                v
     Three-agent visual refinement loop
  +----------------------------------------+
  | 1. Blender Control Agent               |
  |    creates/updates a constrained plan  |
  |                  |                     |
  |                  v                     |
  |       Blender build + preview render   |
  |                  | screenshots         |
  |                  v                     |
  | 2. Visual Judge Agent                  |
  |    produces a detailed defect report   |
  |                  |                     |
  |                  v                     |
  | 3. Correction Recommender Agent        |
  |    converts defects into safe changes  |
  |                  |                     |
  |                  +----> Agent 1        |
  +----------------------------------------+
                |
          accepted scene plan
                |
                v
     Blender lighting bake and GLB export
            /                 \
           v                   v
 mesh_to_splat.py       make_collider.py
           |                   |
           v                   v
 scene_splat.ply         collider.glb
            \                 /
             v               v
         validation, manifest, viewer, Unity
```

The deterministic pipeline remains the source of truth. The agents can choose or revise supported parameters, but they cannot bypass schema validation, invent unsupported object types, or directly replace the export contracts.

## 4. AI architecture: three specialized agents

PromptSplat uses three logical AI agents. Specialization is intentional: scene manipulation, visual criticism, and correction planning require different context and different output contracts. Keeping them separate also makes every iteration auditable.

### 4.1 Agent 1: Blender Control Agent

The Blender Control Agent is responsible for turning the user’s request into a valid scene and controlling the Blender build process. It owns the current scene plan and is the only agent allowed to request scene changes.

Its responsibilities are:

- Interpret the original user prompt.
- Select one supported plan type: standalone building, city block, or general prop scene.
- Produce or revise schema-valid JSON.
- Invoke validation and deterministic auto-repair.
- Run Blender to create the scene.
- Render a fixed set of diagnostic views.
- Apply approved corrections from the Correction Recommender Agent.
- Preserve the user’s original intent while making corrections.
- Stop when the scene passes the acceptance criteria or reaches the iteration limit.

Agent 1 should prefer semantic edits such as `floors`, `footprint.width`, `roof.type`, `num_lanes`, material choice, or catalog asset selection. For building and street plans, it must not calculate individual wall or road coordinates. Those coordinates are derived by `buildinggen.py` and `blockgen.py`.

The existing implementation already provides most of this agent’s execution surface:

- `planner/plan.py` performs model selection, plan generation, caching, repair, and validation.
- `planner/prompt_template_v3.txt` constrains what the model may express.
- `blender/builder.py` controls headless Blender and dispatches to deterministic generators.
- `blender/preview_scene.py` produces diagnostic screenshots without the expensive final conversion stages.
- `pipeline/run.py` orchestrates the complete production run.

### 4.2 Agent 2: Visual Judge Agent

The Visual Judge Agent receives the original prompt, the resolved scene plan, geometry warnings, and multiple screenshots of the Blender output. Its only job is to inspect the rendered evidence and produce a detailed defect report. It does not modify the scene and does not recommend implementation changes.

The screenshots should include at least three orbit views and one top-down view. A fixed camera policy is important because it allows findings from different iterations to be compared reliably.

The judge evaluates:

- Prompt alignment: whether the scene contains the requested subject and requested attributes.
- Geometry integrity: disconnected parts, floating objects, gaps, intersections, clipping, or collapsed geometry.
- Scale and proportion: unrealistic relative sizes or dimensions.
- Placement and composition: missing objects, accidental clutter, poor centering, or occlusion.
- Architecture: floor count, windows, doors, roof shape, facade coherence, and building orientation.
- Streets: lane count, lane markings, intersection continuity, sidewalks, lots, and street furniture.
- Materials and color: requested color accuracy, missing materials, excessive darkness, or flat-gray exports.
- Lighting and visibility: underexposure, blown highlights, poor contrast, or a sky dome obscuring the scene.
- Export risk: visual evidence likely to produce sparse, blurry, or oversized splats.

The report should be machine-readable as well as human-readable. A suitable contract is:

```json
{
  "verdict": "pass | revise | fail",
  "overall_score": 0.0,
  "prompt_alignment_score": 0.0,
  "geometry_score": 0.0,
  "appearance_score": 0.0,
  "defects": [
    {
      "id": "D001",
      "severity": "critical | major | minor",
      "category": "geometry | scale | placement | material | lighting | prompt_alignment | camera",
      "views": ["preview_0.png", "preview_3.png"],
      "observation": "What is visibly wrong",
      "expected": "What the prompt or plan requires",
      "evidence": "Where and how the defect appears",
      "confidence": 0.0
    }
  ],
  "accepted_features": [
    "Features that are already correct and must be preserved"
  ]
}
```

The judge must describe only observable defects. It should not infer a code fix, because doing so would mix evaluation with planning and make it harder to tell whether a later correction actually addresses the visual evidence.

### 4.3 Agent 3: Correction Recommender Agent

The Correction Recommender Agent receives the original prompt, current plan, validator output, iteration history, and the Visual Judge Agent’s defect report. It translates the findings into a prioritized, minimal set of corrections for Agent 1.

Its responsibilities are:

- Identify the likely cause of each reported defect.
- Map each correction to a supported plan field or deterministic generator setting.
- Preserve features that the judge marked as correct.
- Prefer the smallest change that resolves the highest-severity defect.
- Avoid oscillation by considering earlier iterations and rejected changes.
- Reject recommendations that violate the schema or exceed supported capabilities.
- Escalate unsupported requests instead of fabricating an object or geometry type.

A suitable correction contract is:

```json
{
  "iteration": 2,
  "summary": "Short explanation of the correction strategy",
  "corrections": [
    {
      "defect_ids": ["D001"],
      "priority": 1,
      "target": "roof.height",
      "operation": "replace",
      "value": 1.4,
      "reason": "The roof dominates the facade in all orbit views",
      "expected_effect": "Lower roof with the requested cottage proportions"
    }
  ],
  "preserve": [
    "facade.material",
    "floors",
    "facade.door_side"
  ],
  "requires_generator_change": false,
  "unsupported_findings": []
}
```

Agent 3 recommends; Agent 1 remains responsible for applying the changes, validating the revised plan, and controlling Blender. This prevents the recommender from making unvalidated direct edits to a Blender scene.

### 4.4 Agent loop and stopping rules

The three agents run as a bounded refinement loop:

1. Agent 1 creates and validates an initial plan.
2. Agent 1 builds a preview scene and renders diagnostic screenshots.
3. Agent 2 judges the screenshots and returns a defect report.
4. If the verdict is `pass`, the plan proceeds to the production bake and export.
5. If the verdict is `revise`, Agent 3 proposes corrections.
6. Agent 1 applies valid corrections and starts the next preview iteration.
7. If the verdict is `fail`, the system records the failure and explains whether it is caused by an unsupported request, an invalid plan, or a Blender execution error.

Recommended default limits are three refinement iterations, no remaining critical defects, no remaining major prompt-alignment defects, and an overall score of at least `0.85`. A scene should also stop early if two consecutive iterations produce no measurable score improvement. This protects cost and latency and prevents circular edits.

Every iteration should be stored under the run directory so the process can be reproduced:

```text
outputs/runs/<run-hash>/
  iterations/
    000/
      plan.json
      previews/
      judge_report.json
      corrections.json
    001/
      plan.json
      previews/
      judge_report.json
      corrections.json
  final_plan.json
  scene_splat.ply
  collider.glb
  manifest.json
```

### 4.5 Current implementation status of the agent loop

The repository contains the Blender control, preview rendering, validation, and manual visual-loop foundations. `scripts/visual_loop.py` already builds test cases, renders preview images, and writes a per-cycle report. The automated multimodal judge and correction-recommender calls are the remaining integration work. At present, preview review and generator correction are performed manually, while `auto_repair_plan()` handles deterministic pre-render parameter repair.

The intended implementation is to extend `scripts/visual_loop.py` or introduce a production `pipeline/agent_loop.py` coordinator without changing the existing Blender, splat, collider, or Unity file contracts.

## 5. Scene-plan layer

### 5.1 Planner and model fallback

`planner/plan.py` loads the active prompt template, calls OpenRouter’s chat-completions endpoint, parses the returned JSON, repairs common errors, validates the result, and caches successful plans.

The model list in `planner/models.py` is ordered by observed planning reliability. If one model is unavailable, rate-limited, returns invalid JSON, or produces an invalid scene, the planner tries the next model. The request temperature is `0.2` to reduce unnecessary variability.

The planner performs two repair paths:

- Syntax repair: when the response is not valid JSON, the same model is asked once to return clean JSON only.
- Semantic repair: after deterministic auto-repair, remaining validation errors are sent back to the model once with the exact error messages.

Successful plans are cached in `outputs/plans` using an MD5 key derived from the prompt, seed, and prompt-template version. Including `TEMPLATE_VERSION` prevents old cached plans from silently surviving a schema or prompt change.

### 5.2 Three scene-plan types

`planner/schema.json` defines three disjoint plan shapes.

#### Standalone building

A building plan contains bounded semantic parameters: footprint, floor count, floor height, facade material, window dimensions and count, door dimensions and side, roof type and height, position, and yaw. The LLM does not place walls, windows, doors, or roof panels individually.

#### City block

A city-block plan contains block dimensions, road width, sidewalk width, lane count, a `straight` or `intersection` layout, optional building lots, and street-furniture toggles. The maximum accepted scene width and depth is 24 metres for predictable render and sampling cost.

#### General prop scene

A prop scene is the legacy flexible path. It contains a ground description, lighting, and an object list. Objects can be basic Blender primitives, semantic recipe types, or identifiers from the offline GLB catalog. This path is retained for non-architectural arrangements that cannot be represented by the building and city-block schemas.

### 5.3 Validation and deterministic repair

`planner/validate.py` first applies JSON Schema validation and then checks semantic rules that JSON Schema alone cannot express.

Important checks include:

- Buildings fit within their assigned lots.
- Windows fit on both facade dimensions without overlapping.
- City blocks stay within the performance ceiling.
- Object types belong to a fixed allow-list.
- Object positions remain within environment bounds.
- Catalog assets remain grounded and normally use unit scale.
- Primitive objects do not extend below the ground.
- Multi-floor legacy structures have plausible wall height.
- Duplicate roofs and externally rotated roof recipes are rejected.
- Raw primitives cannot masquerade as roof or tree recipe types.
- Non-terrain objects stay under the global scale ceiling.
- All scale values are positive.
- Single-asset requests do not acquire unrelated street decoration.

`auto_repair_plan()` handles safe, deterministic corrections before another model call is considered. It fills missing building defaults, clamps footprint and floor parameters, makes buildings fit their lots, clamps window and door dimensions, reduces excessive window counts, limits city-block dimensions, and normalizes lane count. Every repair is logged into the plan metadata.

This is a central design decision: simple numeric errors are fixed by code, not by spending another AI request or asking a model to repeat geometry arithmetic.

## 6. Deterministic Blender implementation

### 6.1 Builder entry point

`blender/builder.py` runs inside Blender’s Python environment. `pipeline/run.py` launches it in background mode and passes a plan path, output GLB path, Cycles sample count, preview count, and preview directory.

The builder performs these operations in order:

1. Configure the Cycles renderer for CPU execution.
2. Load material presets and create required Blender materials.
3. Clear the startup scene.
4. Dispatch the plan to a building generator, city-block generator, or legacy scene builder.
5. Add an outdoor sky dome when appropriate.
6. Configure the light rig.
7. Create a `Col` vertex-color attribute on every mesh.
8. Run post-build geometry checks.
9. Bake combined lighting into vertex colors.
10. Link the color attribute into each material so the glTF exporter retains it.
11. Exclude the lighting-only sky dome and export `scene.glb`.
12. Render orbit and top-down preview images.

The `--no-bake` CLI option currently selects a one-sample fast bake rather than bypassing `bpy.ops.object.bake()` completely.

### 6.2 Building generator

`blender/buildinggen.py` converts a semantic building specification into geometry. It computes total wall height as `floors × floor_height`, creates one main body, derives door placement from the requested wall, and creates window grids from the facade dimensions.

Window positions are calculated per floor and per wall. A ground-floor window slot is skipped when it would overlap the door. Front, back, left, and right walls use fixed orientation rules, so the model never has to supply trigonometry.

The roof is selected through a fixed dispatch table:

- A flat roof is one slab sized from the footprint.
- A slanted roof uses two panels whose tilt is `atan2(roof_height, footprint_width / 2)`, plus triangular gable fills.

If a building has a yaw, every generated part is parented to a pivot at the building origin and the pivot is rotated around Blender’s vertical Z axis. This preserves the relationships between the body, windows, door, and roof.

### 6.3 City-block generator

`blender/blockgen.py` derives the complete street layout from a small set of dimensions.

For a straight layout, it creates one road along Blender’s Y axis, adds evenly spaced lane-divider strips, creates sidewalks on both sides, divides the block into indexed lots, and places lot buildings at computed centres.

For an intersection, it creates a continuous east-west strip and split north-south arms. Lane markings and sidewalks are split around the intersection core to avoid coincident surfaces and z-fighting. Corner-lot centres are derived from the road, sidewalk, and block dimensions.

Building footprints are clamped again at generation time to fit the calculated lot. Optional trees and streetlights are imported from the offline asset library and placed at deterministic intervals.

### 6.4 General scene builder and asset catalog

The general scene path supports cubes, spheres, cylinders, cones, planes, toruses, and the Blender monkey mesh. It also provides semantic recipes for roofs, windows, doors, roads, sidewalks, and simple trees.

Reusable assets are listed in `assets/library/catalog.json` and stored as local GLB files. The current catalog includes furniture, facade parts, road components, street furniture, vegetation, and vehicles. `scripts/create_asset_library.py` regenerates those GLBs programmatically, which keeps Docker builds and offline runs independent of an external asset service.

Flat primitives receive simple subdivision to create enough vertices for a useful vertex-color bake. Curved primitives receive limited Catmull-Clark subdivision. Cylinders and cones use simple subdivision because smoothing their N-gon caps can pinch the geometry.

### 6.5 Materials, lighting, and previews

Named PBR material presets live in `planner/city_materials.json`. Building facade, window, and roof fields may also contain inline RGB, roughness, and metallic values for requested colors not covered by the presets.

Lighting supports daylight, golden hour, overcast, night, and general sun/point/area modes. Night scenes create point lights at streetlight positions. Outdoor scenes receive an inward-facing emissive sky dome sized from the content bounds. The dome participates in the bake and preview but is not exported.

Preview cameras frame the actual content bounds rather than the ground or sky dome. Orbit distance is proportional to the content diagonal, and the final view is top-down. These previews are the input evidence for the Visual Judge Agent.

## 7. Mesh-to-splat conversion

`scripts/mesh_to_splat.py` loads the exported GLB with `trimesh`, resolves scene-graph transforms into world-space meshes, and allocates the requested number of samples across meshes in proportion to surface area.

For each sampled surface point, it computes:

- Position from triangle surface sampling.
- Color from a texture, interpolated vertex color, material base color, face color, or neutral fallback, in that priority order.
- Surface normal from the sampled triangle.
- Orientation quaternion that rotates the Gaussian’s local positive Z axis onto the surface normal.
- Tangential size from the mean distance to the nearest neighbours.
- Normal-axis size as `tangent_size × flatten`, producing a thin disc that hugs the surface.
- Opacity stored in inverse-sigmoid form.
- RGB stored as spherical-harmonic DC coefficients.

Coincident points receive microscopic jitter before neighbour-distance calculation to prevent zero scales and invalid logarithms. Large splats are clamped relative to the median size to avoid sparse or oversized regions dominating the result.

The output is a binary little-endian PLY with exactly 62 float properties per point:

- 3 position values.
- 3 placeholder normal values.
- 3 spherical-harmonic DC color values.
- 45 zeroed higher-order spherical-harmonic values.
- 1 opacity value.
- 3 logarithmic scale values.
- 4 quaternion values.

This layout is compatible with common 3D Gaussian Splatting loaders, including the expected Unity workflow. Because higher-order coefficients are zero, appearance is view-independent; the lighting variation comes from Blender’s baked vertex colors.

## 8. Collider generation

`scripts/make_collider.py` loads the same intermediate `scene.glb`, resolves world transforms, concatenates all mesh parts, removes visual materials, and optionally simplifies the result with `fast_simplification`.

The production pipeline currently requests a face ratio of `0.5`. The collider and splat therefore originate from the same geometry and coordinate system. This is what allows the Gaussian scene to provide the visuals while the GLB provides solid physics in Unity.

## 9. Pipeline orchestration and run artifacts

`pipeline/run.py` is the command-line orchestrator. For each prompt it calculates `MD5(prompt + seed)` and creates a run directory below `outputs/runs`. A successful existing `manifest.json` enables resume mode and prevents redundant work.

The production sequence is:

1. Load a supplied plan or call the planner.
2. Run Blender headlessly to build, bake, export, and render previews.
3. Convert `scene.glb` into `scene_splat.ply`.
4. Convert `scene.glb` into `collider.glb`.
5. Run structural output validation.
6. Write `preview.html` using the `gsplat.js` browser viewer.
7. Write `manifest.json` with the prompt, seed, splat count, duration, status, warnings, and file names.
8. Remove intermediate files unless `--keep-intermediate` is enabled.

The output validation gate confirms that the PLY exists and has the required 62-property layout. It then loads the collider and verifies that it contains non-empty mesh geometry. A failed stage writes a failure manifest rather than silently leaving an apparently complete run.

Batch mode reads one prompt per line, processes them sequentially, and generates an HTML contact sheet with a preview, status, and viewer link for each result.

## 10. Web interface

`pipeline/web_ui.py` exposes the pipeline through Flask.

The interface offers four modes:

- Describe: sends free-form language through the AI planner.
- Building: creates a building plan directly from structured UI controls.
- Street: creates a city-block plan directly from structured controls.
- Object: creates a one-item scene from the catalog.

The last three are “Quick Build” paths. They bypass the planning model, but still run deterministic repair and validation. This makes common supported requests faster and more reliable.

`POST /generate` starts a background pipeline thread. `GET /api/stream/<run_id>` streams Server-Sent Events containing planning, building, baking, and conversion status. `GET /api/catalog` exposes the local asset list, and `/runs/<path>` serves generated previews and artifacts with cache disabled.

Progress is inferred partly from generated-file existence, while the full pipeline runs in the worker thread. Completed run hashes are returned immediately when their manifest already reports success.

## 11. Unity integration

The Unity workflow uses the PLY as the rendered environment and the GLB as its collision shell.

`unity/Editor/PromptSplatImporter.cs` reads a selected run’s manifest, verifies both files, creates a root environment object, and prepares child objects for a splat renderer and a mesh collider. The current editor script leaves placeholder renderer and mesh assignment steps because the final component types depend on the installed Gaussian-splat and glTF packages.

`unity/Runtime/EnvironmentLoader.cs` instantiates a prepared environment prefab and contains a screenshot-orbit harness. It creates a temporary camera, captures evenly distributed views around the environment, and stores the images for computer-vision validation. This complements Blender previews when the final in-engine result also needs evaluation.

## 12. Reliability, caching, and failure handling

PromptSplat uses several independent reliability layers:

- Low-temperature structured planning.
- Ordered model fallback for OpenRouter failures.
- JSON cleanup and one syntax-repair attempt.
- JSON Schema enforcement.
- Semantic validation for geometric relationships.
- Deterministic repair for bounded numeric errors.
- Generator-level clamping for lot fit.
- Post-build Blender geometry checks.
- Multi-view visual judgment in the three-agent loop.
- PLY and collider structural validation after export.
- Prompt-plan caching and successful-run resume behavior.
- Fixed random seeds for reproducible planning and point sampling.

The layers catch different classes of failure. Schema validation catches malformed intent; generator rules prevent invalid construction; screenshots reveal defects that numerical checks cannot see; and output QA protects the file-format contract.

## 13. Testing strategy

The test suite covers the pipeline at multiple levels:

- `test_validate_city_rules.py` exercises semantic validation rules.
- `test_v2_generators.py` checks default repair, clamping, and Blender generator execution.
- `run_in_blender.py` checks generated building dimensions, roof parts, doors, yaw, roads, and lot buildings inside Blender.
- `test_bake.py` verifies that exported meshes contain non-uniform baked vertex colors.
- `test_builder.py` runs cached plans through the Blender builder and validates the resulting GLBs.
- `test_ply_format.py` verifies the complete 62-property PLY schema, binary payload size, opacity, quaternion normalization, and finite scales.
- `test_collider.py` checks collider loading, geometry, watertightness for the fixture, and simplification.
- `test_pipeline.py` performs an end-to-end run from a fixed plan without a live API call.
- `scripts/visual_loop.py` renders a growing matrix of building, street, material, and catalog cases for visual regression review.

For the full three-agent implementation, each visual-loop case should also have judge expectations and correction assertions. Tests should verify that critical defects decrease between iterations, accepted features do not regress, correction patches remain schema-valid, and the loop stops deterministically.

## 14. Deployment

The native Windows path uses `setup.ps1` and `start.bat` to create a virtual environment, install dependencies, locate or download Blender, configure the API key, open the browser, and start the Flask UI.

The Docker path uses Ubuntu 22.04, installs Blender 5.1.2 and the required headless graphics libraries, installs Python dependencies, builds the offline asset catalog during image creation, and serves the Flask application on port 5000. The host `outputs` directory is mounted into the container so generated scenes survive container restarts.

The API key is the only required external secret for Describe mode. Quick Build modes and fixed plan files do not require a planning request. The future Visual Judge and Correction Recommender agents will require a configured vision-capable model and a text model, or a single multimodal provider exposed through both agent contracts.

## 15. Known constraints and implementation boundaries

- Streets support straight segments and one four-way intersection, not curved or multi-segment road networks.
- Arbitrary objects are not synthesized as high-quality meshes. Unsupported objects must be approximated from primitives or added to the catalog.
- Building generation uses a rectangular footprint and fixed facade logic.
- The visual PLY uses sampled, view-independent color rather than a trained radiance field.
- Surface-area sampling can underrepresent small but important details unless the point budget is large enough.
- Blender CPU baking and repeated visual-agent iterations can be the dominant latency.
- OpenRouter free-model availability and rate limits can affect Describe mode.
- The current automated QA checks file structure, not visual correctness; that is the reason for the Visual Judge Agent.
- The current repository has the manual visual feedback harness, but the automated judge/recommender coordinator still needs to be wired in.
- The Unity editor integration prepares placeholders and still requires the project’s selected splat and glTF packages for final component assignment.

## 16. Recommended implementation sequence for completing the agent system

1. Add versioned JSON Schemas for judge reports and correction recommendations.
2. Add `pipeline/agent_loop.py` as the sole coordinator of agent state and iteration folders.
3. Reuse `blender/preview_scene.py` for fast evidence generation before the expensive production bake.
4. Implement the Visual Judge Agent with multi-image input and strict structured output.
5. Implement the Correction Recommender Agent with access to the current plan, defect report, schema, and prior iteration history.
6. Let the Blender Control Agent apply corrections through an allow-listed JSON Patch layer, followed by `auto_repair_plan()` and `validate_plan()`.
7. Add scoring, maximum-iteration, no-improvement, and unsupported-request stopping rules.
8. Persist all prompts, reports, corrections, model identifiers, timings, and plan hashes in the run manifest.
9. Extend the visual regression cases to test judge consistency and correction effectiveness.
10. Only after a plan is accepted, call the existing production pipeline to bake, create splats, build the collider, and run final QA.

This sequence preserves the tested export pipeline and adds the requested intelligence at the preview-and-revision boundary, where it can improve visual quality without weakening deterministic geometry or output compatibility.
