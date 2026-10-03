> 本文件的 `docs/`、`tasks/`、`work/`、`scripts/` 路徑範例描述建模工作區。安裝本 skill 後，規範位於 `references/`、驗證器位於 `scripts/validate_task.py`、模板位於 `assets/templates/`；以本 skill 的實際絕對路徑解析，勿假設使用者工作區已有這些檔案。

# AI / Codex Blockbench Modeling Specification v1.0

> Checked against current public Blockbench/OpenAI documentation on 2026-10-01.

## 1. Purpose

任務型知識庫告訴人「好模型的原理」；本層把原理轉成 Codex 可執行、可驗證的施工合約。

```text
Design intent
→ measurable blueprint
→ generated model
→ mechanical validation
→ visual QA
→ revision
```

第一版永遠只是 Blockout，不視為成品。

## 2. 五層來源

每個模型任務至少有：

```text
A. REFERENCE NOTES — 真實作品能學什麼、不能抄什麼
B. DESIGN DNA      — 輪廓、材質、焦點、世界觀
C. MODEL_TASK.toml — 精確尺寸與 Production Contract
D. FORMAT TEMPLATE — 當前 Blockbench/Minecraft 格式模板
E. VISUAL QA       — Render/Screenshot/In-game 審查證據
```

不要把五層全塞進一個超長 prompt。

## 3. 先鎖定 Blockbench format

不同格式能力不同。任務必須明確指定，例如：

```text
java_block_item
geckolib_item
geckolib_armor
geckolib_entity
bedrock_entity
modded_entity
generic_reference_only
```

若功能不被目標格式支援，先換工作流，不要硬建。

官方 format matrix：
https://blockbench.net/wiki/blockbench/formats/

## 4. `.bbmodel` 安全規則

Blockbench 官方將 `.bbmodel` 描述為 JSON-based 內部專案格式，可能有 breaking changes，且目前沒有完整正式規格。因此：

```text
BAD  : 從記憶完整手寫 bbmodel
BETTER: 修改目前版本 seed bbmodel，保留未知欄位
BEST : 以 task spec 為 source of truth，經 Blockbench/plugin/export 工作流產出目標檔
```

官方：
https://blockbench.net/wiki/docs/bbmodel/

## 5. 真實作品參考協議

每個 Hero Asset 盡量找 2–5 個來源。只記錄：
- 作品、作者、URL、License/限制
- silhouette / proportion / value grouping / pivot / display / timing 能學什麼
- 明確列出不可複製：geometry、UV、texture pixels、獨特 ornament、1:1 silhouette

正確轉化：

```text
A 教負空間
B 教高亮焦點
C 教第一人稱縮放
→ 自己做不對稱月牙 + 偏心封印核心 + 短下握柄
```

錯誤：`A 的刀刃 + B 的柄 + C 的顏色`。

## 6. Design DNA

建座標前固定：

```text
role
world/faction
primary silhouette
secondary silhouette
focal point
primary material
secondary material
accent material
damage/age
symmetry rule
detail density
```

原則：一個主輪廓、一個輔助輪廓、一個焦點。

## 7. Blueprint first

Codex 不可在生成幾何時臨時猜比例。Task 必須先定義：
- overall bounds
- main axis
- grip/root/attachment
- major part ratios
- cube/bone/plane budget
- minimum detail unit
- texture resolution

例：總長 30、blade 17、head/core 5、grip 8。

## 8. Geometry budget

```toml
[budget]
max_cubes = 18
max_bones = 0
max_planes = 2
min_detail_unit = 1.0
allow_subpixel_geometry = false
```

Budget 是上限，不是必須填滿。優先序：Silhouette → functional joints → secondary forms → small accents。

## 9. Coordinate contract

Cube 必須寫明：id、parent、from/to、pivot、rotation、material、purpose。

```toml
[[parts]]
id = "blade_main"
kind = "cube"
parent = "root"
from = [-1.5, 9.0, -0.5]
to   = [ 1.5, 25.0, 0.5]
pivot = [0.0, 9.0, 0.0]
rotation = [0.0, 0.0, 0.0]
material = "dark_steel"
purpose = "primary blade silhouette"
```

規則：尺寸必須 >0；parent 存在；不可無故超 bounds；裝飾 cube 也必須有 purpose。

## 10. Bone hierarchy

動畫模型先寫骨架，再建 geometry。

```text
root
└─ handle
   ├─ guard_left
   ├─ guard_right
   └─ blade
      └─ blade_tip
```

每根 bone 必須回答：什麼會動？繞哪個關節？誰繼承？哪個 animation 用？答不出來就可能不需要。

## 11. Pivot contract

Pivot 放真正 hinge：jaw hinge、wing root、visor hinge、chain joint、mechanical fold axis。禁止全部丟 model origin。

## 12. Texture contract

Task 必須指定 texture size 與 named palettes，而不是只寫「金屬感」。

```toml
[texture]
width = 32
height = 32
pixel_density = 1.0

[texture.palette.dark_steel]
colors = ["#D0D2CF", "#92958F", "#5B5E5B", "#343735", "#1E201F"]
```

建議起點：16×16 原版／簡單 icon；32×32 RPG item；64×64 複雜 item/entity；更高需寫理由。

Texture 使用 deliberate pixel clusters，不用隨機 noise 代替材質。

## 13. UV contract

至少定義：box/per-face、texture size、overlap policy、mirror policy。Hero Asset 可額外寫每部件 UV table。不可暗中重疊 UV。

## 14. Display contract

Java 靜態 item 必須至少測：

```text
firstperson_righthand / lefthand
thirdperson_righthand / lefthand
gui
ground
fixed
```

Blockbench Display Mode 官方即用於手持、GUI、地面、Item Frame 等情境：
https://blockbench.net/wiki/guides/blockbench-overview-tips/

Task 中 Transform 只是起始值，不等於畫面一定好看。

## 15. Animation contract

先寫動畫語意與節拍再打 keyframe。

```text
0.00 compact
0.10 core wakes
0.20 guard opens
0.35 blade extends
0.45 overshoot
0.55 settle
```

應有 anticipation → action → impact/overshoot → recover/settle。不是每根 bone 都必須動。

## 16. Runtime trigger contract

動畫 ≠ 遊戲邏輯。Task 必須寫：runtime state、damage/projectile 事件、particle/sound timing。

例：`attack_slam` 在 0.78s hit、0.80s impact particle/sound。

## 17. Output contract

Task 列出預期檔案；沒真的建立就不能宣稱存在。

Java item 例：
```text
work/weapon.bbmodel
assets/<modid>/models/item/weapon.json
assets/<modid>/textures/item/weapon.png
```

GeckoLib entity 例：
```text
assets/<modid>/geckolib/models/entity/x.geo.json
assets/<modid>/geckolib/animations/entity/x.animation.json
assets/<modid>/textures/entity/x.png
```

## 18. Mechanical validation

隨附驗證器只涵蓋其中部分檢查；目前未驗證 display policy/QA、旋轉後 bounds、輸出存在性或目標遊戲格式限制，須另行檢查。

先機械驗證，再談好不好看：
- TOML parse
- required fields
- unique IDs
- valid parents
- positive dimensions
- budget
- valid hex palette
- display vec3
- unique animations
- expected outputs

執行：`python scripts/validate_task.py <task.toml>`。

機械 PASS 不代表視覺 PASS。

## 19. Visual QA views

Hero model 最少：front、side、back、3/4、silhouette。

Item 再加：first-person、third-person、GUI、ground、fixed。
Entity 再加：idle、locomotion contact、attack anticipation、attack impact。

## 20. Visual QA 判定

### Silhouette
PASS：縮圖仍讀得出類型、主要負空間清楚。FAIL：像 generic stick/box 或重要部件糊成一團。

### Proportion
PASS：比例符合 blueprint。FAIL：生成中臨時改尺寸。

### Detail hierarchy
PASS：先讀大形再讀小細節。FAIL：微型 geometry 搶走主輪廓。

### Minecraft style
PASS：pixel density coherent、geometry economical、surface detail 交給 texture。FAIL：大量微型 cube、隨機平滑 gradient/noise。

### Usability
PASS：第一人稱不遮中心、entity 關節不脫節、wearable 關鍵 pose 不明顯穿模。

## 21. Defect / revision protocol

禁止只寫「更酷、更細節」。寫 measurable defect：

```text
DEFECT-01
severity = blocking
view = firstperson_righthand
observation = blade covers crosshair
cause = scale/x translation
change = scale 0.75→0.62; x translation +1.5
```

## 22. 三階段生產

### Pass A — Blockout
只做大 geometry、灰階/flat、核心 pivot、基本 display。目標：證明 silhouette/proportion。

### Pass B — Structural polish
Secondary forms、正確 pivot、UV、display、animation mechanics。目標：證明 function。

### Pass C — Surface polish
Final palette/material、restrained wear、emissive accent、timing polish。目標：完稿，但不改核心設計。

Pass A 不過，不准直接跳 C。

## 23. Codex task prompt

```text
Create the model described by tasks/<asset>.task.toml.
Follow AGENTS.md and docs/AI_MODELING_SPEC.md.
Run the validator first.
Do not invent a new bbmodel structure: inspect/preserve the supplied current-version seed project.
Implement Pass A only on the first iteration.
Produce QA renders/screenshots if the environment supports them; otherwise mark visual QA pending.
Do not add decorative geometry outside the task spec.
```

OpenAI Codex 支援透過 `AGENTS.md` 提供 repo 持久指示；較大的知識應放結構化 docs，讓 `AGENTS.md` 作為導航，而不是百科正文。

OpenAI references:
https://openai.com/index/introducing-codex/
https://openai.com/index/harness-engineering/

## 24. Stop conditions

遇到以下情況停止並回報，不准猜：
- target format 未指定
- 非動畫 format 卻要求骨骼動畫
- 需要手寫 bbmodel 但沒有 current seed/template
- 要重用第三方 asset 但 License 不清楚
- dimensions 與 bounds 衝突
- 必要 runtime/plugin 不清楚
- 要求視覺 QA 但無 render/screenshot 管線：保留已完成的可驗證產出，標記視覺 QA pending；不得宣稱完稿驗收通過

## 25. 最低合約

Static item：format、bounds、axis、grip、parts、budget、texture、UV、display、outputs、QA。
Animated item：再加 bones、pivots、animations、beats、triggers/effects。
Entity：再加 body plan、scale、locomotion、hitbox、runtime states、projectile origin。
Wearable：再加 attachment region、body reference、clipping poses、layer compatibility。

## 26. 推薦 repo 結構

```text
AGENTS.md
docs/AI_MODELING_SPEC.md
knowledge-base/
  weapons.md
  equipment.md
  creatures.md
tasks/current_asset.task.toml
templates/MODEL_TASK.template.toml
examples/
scripts/validate_task.py
work/seed.bbmodel
work/renders/
assets/...
```

這一層不能取代 art direction 與視覺判斷；它的目的，是讓 Codex 不再自由猜比例與技術結構，並強制進入可量測的 Render QA 迴圈。


---

## 31. Display calibration subsystem

All item, weapon, wearable, and display-sensitive tasks must also follow:

`[DISPLAY_CALIBRATION.md](DISPLAY_CALIBRATION.md)`

The key rule is:

```text
all/most views wrong → fix geometry
one/few views wrong → fix display context only
```

Calibration order is always:

```text
rotation → translation → scale
```

The task must declare a primary display context and whether base geometry is locked
during display calibration.
