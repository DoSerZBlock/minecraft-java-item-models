# GrayDay VFX Modeling Specification v0.1

## 1. Purpose

```text
Design intent
→ measurable VFX task
→ Pass A blockout
→ asset validation
→ runtime integration
→ Paper QA
→ measurable revision
```

第一版永遠只是 blockout，不視為成品。

## 2. Supported VFX families

v0.1 主要支援：

- projectile
- beam / ray
- area / ground effect
- cast / charge effect
- impact / explosion presentation
- orbiting / attached effect
- summon presentation
- channel effect

若實際需求不符合這些類型，先定義 lifecycle 與 space contract，再新增類型，不要硬套 projectile。

## 3. Design contract

每個 VFX 至少固定：

- gameplay-readable role；
- theme / element；
- primary silhouette；
- focal point；
- material language；
- detail density；
- scale / bounds；
- VFX family。

視覺設計不可自行新增世界觀事實；世界觀與國家/流派設定以 GrayDay 專案文件為準。

## 4. Spatial contract

必須明確區分：

```text
world_space
caster_space
view_space
target_space
velocity_space
```

Task 至少描述 spawn_space、orientation_space、target_space。座標空間不能靠 implementation 猜測。

## 5. Geometry / axis contract

模型至少定義：

- units；
- asset_forward_axis；
- asset_up_axis；
- origin；
- pivot/hinge（若有動畫）；
- bounds / max extent。

合法 axis：`+x -x +y -y +z -z`。

Projectile 的「尖端方向」必須與 asset_forward_axis 一致。若 BetterModel 匯出後方向不同，修 exporter/adapter mapping 或 task，不用 runtime magic number 掩蓋。

## 6. Orientation contract

Task 必須指定 runtime forward source：

- `look_direction`
- `velocity`
- `target_vector`
- `fixed`

以及 follow_yaw / follow_pitch / follow_roll。

Projectile 的預設策略：

```text
spawn: caster look direction
flight: velocity direction
roll: locked unless art direction requires it
```

詳見 ORIENTATION_CALIBRATION.md。

## 7. Motion contract

Motion 是 GrayDay_VFX presentation runtime 的責任。Task 可描述：

- motion type；
- initial speed；
- acceleration；
- max distance；
- arc / homing presentation policy（若有）。

若 motion 會影響 RPG hit resolution，必須透過既有 Core ↔ VFX contract 回報 hit/impact context，不可在 task 內計算 damage。

## 8. Timeline contract

至少包含：

- cast start；
- release；
- travel/channel；
- impact trigger；
- aftermath；
- cleanup。

時間軸描述 presentation timing，不持有 RPG 數值。詳見 ANIMATION_TIMING.md。

## 9. Lifecycle contract

每個 instance 都必須能處理：

```text
COMPLETED
CANCELLED
EXPIRED
FAILED
DISPOSED
```

至少明確定義：

- dispose_on_impact；
- dispose_on_cancel；
- dispose_on_disconnect；
- dispose_on_shutdown；
- timeout / max lifetime。

## 10. Effects contract

Particle、Sound、Model、Animation 以 stable identifier 引用。避免把大量 implementation-specific 參數散落在多個 repo。

Impact effect 是 presentation。最終 RPG 結果由 GrayDay_Core 決定。

## 11. Performance budget

每個 task 至少限制：

- max models per cast；
- max particles per tick；
- max active instances per player；
- max lifetime；
- 是否允許 per-viewer fan-out。

Budget 是上限，不是填滿目標。視覺優先序：

```text
readability
→ silhouette / motion
→ impact cue
→ secondary particles
→ micro detail
```

## 12. Repository output contract

GrayDay_Assets 保存正式 client asset source；GrayDay_VFX 保存 runtime composition/integration；GrayDay_Core 保存 RPG ability/domain definition。

Skill 可以一次規劃跨 repo 產出，但不可複製 domain source of truth。

## 13. Forbidden domain data

VFX task 不得定義：

- damage / healing；
- mana/resource cost；
- cooldown；
- crit chance/multiplier；
- stat scaling；
- skill rank balance。

若需要關聯，使用 ability_id、correlation_id、presentation_id 等 identifier。

## 14. Production passes

### Pass A — Blockout
Silhouette、scale、axis、origin。

### Pass B — Structure / Orientation
Pivot、bone、attachment、runtime orientation。

### Pass C — Surface / Animation
Texture、material、animation、particle/sound polish。

### Pass D — Runtime
Motion、collision presentation、lifecycle、cleanup。

### Pass E — Paper QA
Horizontal、pitch up/down、side、impact、timeout、disconnect、cleanup。

Pass A/B 未通過，不進行高成本 surface polish。

## 15. Defect protocol

所有 blocking 問題都用可重現 case 記錄：

```text
case
observation
expected
suspected cause
allowed layer to change
result
```

先判斷根因層：

```text
all views wrong      → asset geometry / axis
flight only wrong    → runtime transform
pitch only wrong     → pitch/orientation mapping
impact only wrong    → impact spawn/pivot
cleanup only wrong   → lifecycle
```

## 16. Completion

Validator PASS 只代表 contract 靜態一致。真正完成仍需 visual QA 與 Paper runtime evidence。
