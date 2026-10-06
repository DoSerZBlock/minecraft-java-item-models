# GrayDay VFX Orientation Calibration v0.1

## Core principle

不要混淆「模型本身的 forward axis」與「遊戲世界裡目前要朝向的 vector」。

```text
asset_forward_axis + runtime_forward_vector + up policy
→ runtime rotation
```

## Required axis declaration

每個模型必須宣告：

```toml
[geometry]
asset_forward_axis = "+z"
asset_up_axis = "+y"
origin = "rear_center"
```

Projectile 尖端必須位於 forward axis 的正方向。

## Runtime forward sources

- `look_direction`：施法者視線。
- `velocity`：目前 motion velocity；一般 projectile 優先。
- `target_vector`：spawn → target。
- `fixed`：world/static presentation。

不要用 world-horizontal 當 projectile 的隱含預設。

## Yaw / Pitch / Roll

- yaw：水平轉向；
- pitch：抬頭/低頭；
- roll：繞 forward axis 自轉。

一般霜槍類 projectile：

```text
follow_yaw   = true
follow_pitch = true
follow_roll  = false
```

若玩家向上/下看但 projectile 保持水平，這是 blocking runtime defect。

## Head-tail inversion

症狀：

- velocity 正確，但模型屁股朝前；
- 模型沿路徑倒著飛。

優先檢查：

1. task 的 asset_forward_axis 是否與模型實際尖端一致；
2. BetterModel Adapter 的 coordinate mapping；
3. runtime quaternion/lookAt 的 forward convention；
4. 是否額外加了 180° magic rotation。

不要在多個 layer 同時加 180° offset。

## Calibration matrix

至少測：

| Case | Input | Expected |
| --- | --- | --- |
| horizontal | pitch 約 0° | 尖端沿 velocity |
| pitch_up | +45° 或更高 | 模型抬頭跟隨 |
| pitch_down | -45° 或更低 | 模型低頭跟隨 |
| yaw_left/right | 改變 yaw | 無固定 world direction |
| side_observation | 第三者側面觀看 | forward 與 trajectory 一致 |

若水平 PASS、pitch up/down FAIL，先修 runtime pitch transform，不改 asset geometry。

## Spawn vs flight

允許：

```text
spawn orientation = caster look direction
flight orientation = velocity
```

這能避免初始 velocity 尚未穩定時的 undefined orientation。

## Defect examples

```text
ORIENT-01
case = pitch_down
observation = model stays horizontal
expected = forward follows velocity
layer = GrayDay_VFX orientation
geometry_change = false
```

```text
ORIENT-02
case = horizontal
observation = tail points toward target
expected = tip points toward target
layer = asset axis or adapter mapping
geometry_change = conditional
```

## Completion

Blocking cases 全部通過後才鎖定 orientation。後續修改 base geometry、pivot 或 adapter mapping 時，必須重跑完整 orientation matrix。
