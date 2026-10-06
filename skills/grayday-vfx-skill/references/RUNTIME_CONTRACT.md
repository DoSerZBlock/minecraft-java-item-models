# GrayDay VFX Runtime Contract v0.1

## Ownership

```text
GrayDay_Core
  Ability / Resource / Cooldown validation
  Damage / Healing / Buff / Debuff
        ↓ identifiers + callbacks
GrayDay_VFX
  Model / Motion / Collision / Presentation / Lifecycle
        ↓ model IDs
GrayDay_Assets
  BetterModel / Texture / Client assets
```

## Allowed VFX task data

- ability/presentation identifier；
- model identifier；
- spawn/orientation/motion；
- collision presentation policy；
- particle/sound identifiers；
- animation/timeline；
- lifecycle；
- performance budget；
- QA。

## Forbidden VFX task data

- damage；
- healing amount；
- mana/resource cost；
- cooldown；
- crit chance/multiplier；
- stat scaling；
- progression/rank balance。

禁止建立第二套 RPG rule engine。

## Lifecycle

每個 VFX instance 必須經由統一 runtime 結束：

```text
CREATED
→ RUNNING
  → COMPLETED
  → CANCELLED
  → EXPIRED
  → FAILED
→ DISPOSED
```

所有 terminal path 都必須 dispose model/runtime references。

## Required cleanup cases

- normal impact；
- max lifetime / timeout；
- explicit cancel；
- caster disconnect；
- plugin disable / server shutdown；
- runtime exception。

## Collision

Collision resolver 可以產生 hit/impact context，但不計算最終 damage。跨 repo 整合使用穩定 callback/contract，不使用 command relay。

## BetterModel boundary

GrayDay_VFX 透過 ModelProvider adapter 使用 BetterModel；task 只依 stable model ID 參照 GrayDay_Assets。第三方 BetterModel type 不應洩漏到 Core domain。

## Failure semantics

BetterModel unavailable、model missing、spawn failure、runtime exception 必須：

1. 提供可診斷 failure reason；
2. 不留下 orphan model；
3. 走 terminal callback；
4. cleanup；
5. 不偷偷 fallback 到不同 RPG 行為。

## Performance

集中式 tick loop 下，任何 per-instance 工作都要有 budget。避免：

- 每 instance 建 scheduler；
- 無上限 particle fan-out；
- 無 timeout model；
- 每 tick 重複昂貴 asset lookup；
- collision 與 rendering 強耦合。
