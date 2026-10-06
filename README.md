# GrayDay VFX Skill

GrayDay VFX Skill 是由 [wagcies444/minecraft-java-item-models](https://github.com/wagcies444/minecraft-java-item-models) 衍生的 Codex skill，專門用於「灰日世界」Minecraft RPG 的技能視覺效果生產流程。

本 fork 保留原專案的 MIT License 與版權聲明。上游原始 item-model skill 目前仍保留在 `skills/minecraft-java-item-models/`，方便追溯與同步；GrayDay 正式使用的入口是：

```text
skills/grayday-vfx-skill/
```

## 目標

把技能特效從自由描述改成可驗證的 production contract：

```text
Design intent
→ VFX_TASK.toml
→ Blockout / asset
→ orientation + timeline QA
→ GrayDay_VFX runtime integration
→ Paper runtime QA
→ revision
```

## GrayDay repository 邊界

| Repository | Source of Truth |
| --- | --- |
| GrayDay_Core | Ability、Stats、Damage/Healing、Resource、Cooldown、Buff/Debuff 等 RPG Domain |
| GrayDay_VFX | Model actor、Motion、Collision、Particle、Sound、Impact presentation、Lifecycle/Cleanup |
| GrayDay_Assets | BetterModel .bbmodel、texture、sound、UI/client assets |

VFX task **不得**定義 damage、healing、mana/resource cost、cooldown、crit、stat scaling 等 RPG 數值。

## 安裝

在支援 skill installer 的 Codex 環境中，從本 repository 安裝：

```text
$skill-installer 請從 https://github.com/DoSerZBlock/minecraft-java-item-models 安裝 skills/grayday-vfx-skill
```

或將整個 `skills/grayday-vfx-skill/` 複製到專案的 `.agents/skills/`。

## 內容

- `SKILL.md`：GrayDay VFX 生產流程。
- `assets/templates/VFX_TASK.template.toml`：VFX 任務合約模板。
- `assets/example/frost_lance.task.toml`：霜槍 benchmark。
- `references/VFX_MODELING_SPEC.md`：建模、runtime、QA 主規範。
- `references/ORIENTATION_CALIBRATION.md`：模型軸向、yaw/pitch/roll 與 projectile 朝向。
- `references/ANIMATION_TIMING.md`：cast / release / travel / impact / aftermath 時間軸。
- `references/RUNTIME_CONTRACT.md`：Core / VFX / Assets 責任邊界與 lifecycle。
- `references/GRAYDAY_ART_DIRECTION.md`：灰日世界共通視覺方向。
- `scripts/validate_vfx_task.py`：task 靜態驗證。

## 驗證

Python 3.11+：

```bash
python skills/grayday-vfx-skill/scripts/validate_vfx_task.py \
  skills/grayday-vfx-skill/assets/templates/VFX_TASK.template.toml \
  skills/grayday-vfx-skill/assets/example/frost_lance.task.toml
```

Validator PASS 代表 contract 結構、禁止欄位、axis/space、timeline、budget 與必要 Paper QA cases 通過；**不代表視覺品質或 Paper runtime 已通過**。

## v0.1 benchmark

第一個 benchmark 是 `frost_lance`，阻擋條件包含：

- projectile 頭部必須朝 velocity / look direction；
- 玩家向上或向下看時，模型必須跟隨 pitch；
- 不可只在 world-horizontal 飛行；
- 不可 head-tail inversion；
- impact / timeout / disconnect 都必須 cleanup。

## License

本 fork 依原專案 MIT License 使用與修改。Copyright (c) 2026 wagcies444。
