> 本文件的 `docs/`、`tasks/`、`work/`、`scripts/` 路徑範例描述建模工作區。安裝本 skill 後，規範位於 `references/`、驗證器位於 `scripts/validate_task.py`、模板位於 `assets/templates/`；以本 skill 的實際絕對路徑解析，勿假設使用者工作區已有這些檔案。

# DISPLAY_CALIBRATION.md
## Blockbench / Minecraft Display Calibration Specification v1.1

This document defines the mandatory display-calibration workflow for AI-generated
Minecraft items, weapons, equipment, and other models that have multiple render contexts.

The goal is to prevent a common failure mode:

```text
one view looks wrong
→ AI edits the base geometry
→ every other view becomes wrong
```

Display calibration must be treated as a separate production stage.

---

# 1. Core rule

Use this decision:

```text
ALL OR MOST VIEWS LOOK WRONG
→ revise model geometry / proportions

ONLY ONE OR A FEW VIEWS LOOK WRONG
→ revise those display contexts only
```

Do not modify base geometry merely to fix a single first-person, GUI, ground,
or item-frame presentation problem.

---

# 2. Calibration order

For each display context, always tune in this order:

```text
1. Rotation
2. Translation
3. Scale
```

Reason:

- Rotation establishes readable orientation.
- Translation places the model in the correct screen/body region.
- Scale is the final framing adjustment.

Do not use scale as the first fix for an orientation problem.

---

# 3. Required display contexts

For a normal Java item, evaluate:

```text
firstperson_righthand
firstperson_lefthand
thirdperson_righthand
thirdperson_lefthand
gui
ground
fixed
```

Add other contexts if the runtime requires them.

For Bedrock attachables / custom renderers, use equivalent hand/body attachment views.

---

# 4. Primary context

Every task must declare:

```toml
[display_policy]
primary_context = "firstperson_righthand"
```

Examples:

```text
PvP weapon
→ firstperson_righthand

RPG boss drop / showcase weapon
→ thirdperson_righthand

collectible / relic
→ gui or fixed

wearable
→ thirdperson / body attachment

projectile
→ world-flight presentation
```

The primary context receives the strictest QA, but other contexts still need to pass.

---

# 5. Geometry preservation rule

Each task must declare:

```toml
preserve_model_geometry_during_display_calibration = true
```

When true, Codex must NOT:

- move base cubes,
- resize base cubes,
- change blade/handle proportions,
- alter pivots,
- delete parts,

while fixing display QA.

Allowed changes during display calibration:

```text
display rotation
display translation
display scale
display-specific runtime transform
display-specific model override, if explicitly permitted
```

If the only valid fix requires geometry changes, Codex must report:

```text
DISPLAY QA BLOCKED BY BASE GEOMETRY
```

and return to structural revision.

---

# 6. First-person calibration

First-person presentation has four priorities:

```text
1. crosshair / central combat area remains usable
2. grip appears connected to the player's hand
3. weapon silhouette remains recognizable
4. model does not dominate the screen unnecessarily
```

## 6.1 First-person tuning sequence

```text
A. Rotate until the primary silhouette is readable.
B. Translate away from the screen center.
C. Scale down only as much as necessary.
D. Re-check grip/hand relationship.
```

## 6.2 Typical failures

### Failure: blade crosses the crosshair

Prefer:

```text
translation outward
→ slight rotation
→ scale reduction
```

in that order.

### Failure: weapon is technically visible but looks tiny

Prefer:

```text
translation toward usable corner
→ slight scale increase
```

rather than changing the whole model.

### Failure: grip floats away from hand

Usually fix:

```text
translation
rotation
```

not geometry.

---

# 7. Left-hand calibration

Do not assume that right-hand values can be mirrored blindly.

Especially inspect:

- asymmetric scythes,
- shields,
- gunblades,
- one-sided axes,
- claw weapons,
- off-hand tools.

Required:

```text
firstperson_lefthand screenshot / render
thirdperson_lefthand screenshot / render
```

If runtime mirrors automatically, document that fact in the task spec.

---

# 8. Third-person calibration

Third-person priorities:

```text
1. correct grip point
2. believable relationship to player body
3. readable silhouette at gameplay distance
4. no major clipping through torso/head
5. correct perceived size
```

Test at least:

```text
idle
walk
attack / use pose when applicable
```

A large weapon may deliberately be visually larger in third person than in first person.

That is allowed.

---

# 9. GUI calibration

GUI is a composition problem, not a realism problem.

Priorities:

```text
1. identify item category immediately
2. fit inside slot
3. preserve dominant silhouette
4. focal point remains visible
5. avoid edge clipping
```

Examples:

```text
Scythe
→ show crescent and negative space

Hammer
→ head must remain visually dominant

Dagger
→ avoid shrinking to a thin line

Chakram
→ central negative space must remain visible
```

GUI rotation is allowed to differ substantially from hand rotation.

---

# 10. Ground calibration

Ground priorities:

```text
1. model does not sink deeply into ground
2. item scale feels like a dropped item, not a structure
3. recognizable face/silhouette is visible
4. pivot/origin does not create awkward hovering
```

Large RPG weapons usually require aggressive scale reduction here.

---

# 11. Fixed / Item Frame calibration

Fixed is useful for:

- relics,
- trophies,
- weapons on walls,
- item-frame displays,
- shop displays.

Priorities:

```text
1. centered composition
2. readable orientation
3. consistent display scale
4. no frame clipping
```

A hero relic may be framed more dramatically than its GUI view.

---

# 12. Calibration metrics

The following metrics can be used in task specs.

## 12.1 Center obstruction

```text
none
low
medium
high
```

Weapons intended for combat should normally target:

```text
first person → none or low
```

## 12.2 Slot occupancy

For GUI:

```text
min_slot_fill = 0.55
max_slot_fill = 0.90
```

Interpretation:
roughly 55–90% of the available slot area should be used by the main silhouette.

## 12.3 Screen occupancy

For first person:

```text
max_screen_width_fraction
max_screen_height_fraction
```

These are QA targets, not exact physical measurements unless the render pipeline
can measure them.

## 12.4 Crosshair clearance

```text
crosshair_must_remain_clear = true
```

This is a blocking QA rule for combat items unless explicitly overridden.

---

# 13. Display QA schema

Recommended TOML:

```toml
[display_policy]
primary_context = "firstperson_righthand"
calibration_order = ["rotation", "translation", "scale"]
preserve_model_geometry_during_display_calibration = true
allow_display_specific_geometry_override = false

[display_qa.firstperson_righthand]
crosshair_must_remain_clear = true
max_center_obstruction = "low"
must_show_grip_connection = true
must_preserve_primary_silhouette = true

[display_qa.thirdperson_righthand]
must_show_grip_connection = true
must_avoid_major_body_clipping = true
must_preserve_primary_silhouette = true

[display_qa.gui]
must_fit_slot = true
must_preserve_primary_silhouette = true
must_show_focal_point = true
min_slot_fill = 0.55
max_slot_fill = 0.90

[display_qa.ground]
must_avoid_ground_intersection = true
must_read_as_dropped_item = true

[display_qa.fixed]
must_fit_frame = true
must_preserve_primary_silhouette = true
```

---

# 14. Display defect record

Every failed view must produce a measurable defect.

Template:

```text
DISPLAY-DEFECT-01
severity = blocking
context = firstperson_righthand
observation = blade overlaps center crosshair
suspected_cause = x translation too small; weapon scale slightly too large
allowed_change = display only
change_1 = translation.x +1.5
change_2 = scale 0.70 → 0.62
geometry_change = false
result = pending
```

Bad defect report:

```text
weapon looks weird
make it cooler
```

---

# 15. Display iteration stages

## Stage D0 — Initial values

Use rough values from:
- a known-good template,
- a comparable existing item,
- or the task blueprint.

Do not claim these values are final.

## Stage D1 — Primary context

Calibrate the declared primary context first.

Example:

```text
firstperson_righthand
```

Lock it when blocking issues are resolved.

## Stage D2 — Paired context

Then calibrate the paired context:

```text
left hand
or
third person
```

Do not break D1.

## Stage D3 — GUI

Tune separately for icon readability.

## Stage D4 — Ground / Fixed

Tune world-display contexts.

## Stage D5 — In-game verification

Blockbench preview is not enough.

Verify in Minecraft when possible:
- FOV
- arm position
- use animation
- attack swing
- item frame
- dropped item

If Minecraft was not run, explicitly mark:

```text
in_game_display_qa = pending
```

---

# 16. When to go back and change geometry

Return to geometry if ANY of these occur:

```text
- every context needs extreme scaling to look acceptable
- grip cannot be aligned without destroying silhouette
- GUI cannot show the item category at any reasonable rotation
- first and third person both reveal fundamentally bad proportions
- model center/origin is structurally wrong
- important parts are outside the declared bounds
```

Then log:

```text
DISPLAY QA → STRUCTURAL REVISION
```

After structural revision, recalibrate all display contexts.

---

# 17. Context-specific geometry override

Normally disabled:

```toml
allow_display_specific_geometry_override = false
```

Enable only for advanced runtimes where separate GUI/held/world models are intentional.

Example:

```text
Inventory
→ 2D sprite

Held
→ 3D model

Projectile
→ separate flight model
```

If enabled, document each override explicitly.

---

# 18. Codex instruction block

Use this in model tasks:

```text
During display calibration:
- do not alter base geometry unless display QA proves the geometry itself is the root cause;
- tune rotation first, translation second, scale third;
- calibrate primary context first;
- inspect right and left hand separately;
- treat GUI as a separate composition;
- record every failed view as a DISPLAY-DEFECT item with measurable changes;
- re-run all previously passing display views after any base-geometry revision.
```

---

# 19. Display completion checklist

```text
□ primary context passes
□ paired hand/context passes
□ third-person grip is believable
□ GUI silhouette is readable
□ ground view does not sink/hover badly
□ fixed/item-frame view fits
□ no display fix accidentally changed base geometry
□ all blocking display defects resolved
□ in-game verification performed OR clearly marked pending
```

---

# 20. Key principle

A Minecraft model does not have one "correct" presentation transform.

A high-quality asset may intentionally use:

```text
first person → smaller and pushed outward
third person → larger and more dramatic
GUI → rotated for iconic silhouette
ground → much smaller
fixed → centered for display
```

Consistency of *identity* matters more than identical transforms.
