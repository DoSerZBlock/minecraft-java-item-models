---
name: grayday-vfx-skill
license: MIT
description: 建立、修改與驗收灰日世界 Minecraft RPG 的技能視覺效果，涵蓋 BetterModel 資產、模型軸向、空間座標、動畫時間軸、GrayDay_VFX runtime、效能預算與 Paper QA；不處理 RPG 傷害、資源、冷卻或爆擊數值。
---

# GrayDay VFX Skill

本 skill 將技能視覺需求轉成可量測、可驗證、可迭代的 VFX production contract。

## 0. Repository boundary

任何工作開始前先維持以下邊界：

- **GrayDay_Core**：Ability、Stats、Damage/Healing、Resource、Cooldown、Buff/Debuff、Class/Archetype、Persistence 與最終 RPG 結果。
- **GrayDay_VFX**：Model actor、Motion、Collision、Particle、Sound、Impact presentation、VFX lifecycle / cleanup。
- **GrayDay_Assets**：BetterModel `.bbmodel`、texture、sound、client assets 的 Source of Truth。

VFX task 不得持有 damage、healing、mana/resource cost、cooldown、crit、stat scaling。若需求包含這些值，引用 Core 的 ability/event identifier，不複製數值。

## 1. 開始工作

依序讀：

1. [VFX Modeling Spec](references/VFX_MODELING_SPEC.md)
2. [Orientation Calibration](references/ORIENTATION_CALIBRATION.md)
3. [Animation Timing](references/ANIMATION_TIMING.md)
4. [Runtime Contract](references/RUNTIME_CONTRACT.md)
5. [GrayDay Art Direction](references/GRAYDAY_ART_DIRECTION.md)

如果是既有技能，再讀目前 GrayDay_Core ability 定義、GrayDay_VFX implementation、GrayDay_Assets model 與使用者已認可的 Paper 截圖/影片。不要讓 skill 自行改寫既有遊戲規則。

## 2. 建立 VFX task

從 `assets/templates/VFX_TASK.template.toml` 建立 task。至少明確指定：

- VFX 類型與設計意圖；
- asset forward/up axis、origin/pivot；
- spawn/orientation/target space；
- yaw/pitch/roll policy；
- motion；
- cast/release/travel/impact/aftermath timeline；
- lifecycle / cleanup；
- particle/sound/model presentation；
- runtime owner 與 asset source；
- performance budget；
- Paper QA cases 與 blocking rules。

執行：

```bash
python <skill>/scripts/validate_vfx_task.py <task.toml>
```

Validator 未通過前，不開始 production implementation。

## 3. Production passes

### Pass A — Blockout

只證明 silhouette、尺度、forward axis、origin/pivot 與主要空間關係。不要先做高密度裝飾。

### Pass B — Structural / Orientation

完成模型結構、bone/pivot（若需要）、forward/up axis，並先通過：

- horizontal；
- pitch up；
- pitch down；
- side view；
- head/tail direction。

多數角度都錯 → 檢查 asset axis / geometry。
只有 runtime flight 錯 → 修 GrayDay_VFX orientation transform，不要旋轉 base geometry 來掩蓋問題。

### Pass C — Surface / Animation

完成 texture、材質、受控 emissive、動畫節拍。動畫必須先有語意節拍，再做 keyframe。

### Pass D — Runtime Integration

在 GrayDay_VFX 串接：

- ModelProvider / BetterModel；
- spawn transform；
- MotionController；
- collision presentation；
- particle/sound；
- impact presentation；
- timeout/cancel/disconnect/shutdown cleanup。

Runtime 不計算最終 RPG damage/healing。

### Pass E — Paper QA

至少測：

- horizontal cast；
- pitch up；
- pitch down；
- side observation；
- impact；
- timeout；
- caster disconnect；
- cleanup。

沒有 Paper 證據時，標記 `paper_runtime_qa = pending`，不得宣稱完稿。

## 4. Orientation rule

永遠分清楚：

```text
asset forward axis
runtime forward vector
spawn space
orientation space
velocity
camera/look direction
```

Projectile 通常以 velocity 為 runtime forward。若是瞬發且 velocity 尚未建立，可用 caster look direction 初始化，但後續 flight orientation 仍應遵循 task contract。

禁止用「在 Blockbench 把模型轉到看起來差不多」取代 runtime orientation 修正。

## 5. Timeline rule

技能 presentation 以事件為中心：

```text
cast/anticipation → release → travel/channel → impact → aftermath → cleanup
```

Visual timeline 可以描述粒子、音效、模型動畫與 impact presentation；最終 damage/healing 由 Core event/callback 決定。

## 6. Defect protocol

不要只寫「怪怪的」。

```text
VFX-DEFECT-01
severity = blocking
case = pitch_down
observation = frost lance remains world-horizontal
expected = model forward axis follows velocity
suspected_cause = runtime pitch transform missing
allowed_change = runtime orientation only
geometry_change = false
result = pending
```

修正後重新測所有先前 PASS case。

## 7. Stop conditions

遇到以下情況停止猜測並標記 blocked/pending：

- 不知道目標 BetterModel / Paper 版本；
- model forward/up axis 無法確認；
- VFX task 要求 RPG damage/resource/cooldown 數值；
- 需要修改既有 `.bbmodel` 但沒有現有 asset/seed；
- collision ownership 不清楚；
- runtime cleanup 無定義；
- 沒有 Paper/runtime 環境卻要求宣稱實機 PASS。

## 8. 完成定義

完成至少代表：

- task validator PASS；
- GrayDay_Assets asset 可追溯；
- GrayDay_VFX runtime 不跨越 Core domain boundary；
- blocking orientation QA 通過；
- impact / timeout / disconnect cleanup 通過；
- performance budget 未被明顯違反；
- Paper QA 有證據，或清楚標記 pending。
