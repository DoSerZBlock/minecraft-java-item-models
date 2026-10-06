# GrayDay VFX Animation & Timing v0.1

## Principle

先定義語意節拍，再做 keyframe、particle 與 sound。

```text
anticipation → release → travel/channel → impact → aftermath → cleanup
```

## Recommended phases

### Cast / Anticipation
玩家應能讀出技能正在形成。可以使用核心亮起、符文聚合、模型展開、短促音效。

### Release
模型或 projectile 真正脫離 caster 的時間點。Release 是 presentation event，不代表 Core 已造成 damage。

### Travel / Channel
Motion、trail、loop animation。避免每 tick 無上限生成新模型。

### Impact
由 collision / target / terminal event 觸發 impact presentation。最終 RPG damage/healing 仍由 Core pipeline 決定。

### Aftermath
短暫 shockwave、殘留霜霧、地面符文等；必須有明確 lifetime。

### Cleanup
停止 animation/particle loop、dispose model、移除 runtime reference。

## Timeline task fields

```toml
[timeline]
cast_start_sec = 0.0
release_sec = 0.20
impact_trigger = "collision"
aftermath_duration_sec = 0.35
```

Impact 可以是事件型 trigger，而不是硬寫固定秒數。

## Synchronization

視覺 hit cue 應與 VFX impact callback 同步；不要另外用獨立 timer 猜 damage 時刻。

同一事件的 model animation、particle、sound 儘量由同一 presentation composition 觸發，降低漂移。

## Animation quality

若有 BetterModel bone animation，至少考慮：

- anticipation；
- action；
- impact / overshoot；
- settle / recover。

不是每根 bone 都需要動。不要用高頻無意義 motion 製造「細節」。

## Cancellation

在 release 前取消與 release 後取消可能有不同 presentation，但兩者都必須進入統一 cleanup。

## Paper QA

時間軸至少觀察：

- cast 是否在 release 前可讀；
- projectile/trail 是否同步；
- impact particle/sound 是否只觸發一次；
- aftermath 是否準時結束；
- cancel/timeout/disconnect 是否停止 loop。
