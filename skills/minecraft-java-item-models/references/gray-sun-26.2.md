# 灰日拾荒短刃：Java 26.2 歷史校準案例

這是一次經遊戲截圖逐步調整的**技術個案**，用於理解物品欄與手持視角如何拆開處理。它不代表灰日世界通用的裝備造型規則；設計新物品時先查該職業、國家或流派的設定。新物品的尺寸、握點與顯示角度要依模型和遊戲畫面重新決定。可編輯範例位於 [assets/example/](../assets/example/)。原案例曾以使用者遊戲截圖迭代；本公開包沒有附該批截圖，本次發布只重新檢查靜態檔案，未重做 Blockbench 或遊戲 QA。

## 資源包結構

```text
pack.mcmeta
assets/gray_sun/items/starter_blade.json
assets/gray_sun/models/item/starter_blade.json
assets/gray_sun/models/item/starter_blade_held.json
assets/gray_sun/textures/item/starter_blade.png
```

Java 26.2 的範例使用 `pack_format: 88`、`min_format: [88, 0]`、`max_format: [88, 0]`。版本依據：[Mojang 的 Java 26.2 發行說明](https://feedback.minecraft.net/hc/en-us/articles/46690753273997-Minecraft-Java-Edition-26-2)。其他版本重新查官方版本資訊。

物品定義用顯示情境選模型：

```json
{
  "model": {
    "type": "minecraft:select",
    "property": "minecraft:display_context",
    "cases": [{
      "when": ["thirdperson_righthand", "thirdperson_lefthand", "firstperson_righthand", "firstperson_lefthand"],
      "model": {"type": "minecraft:model", "model": "gray_sun:item/starter_blade_held"}
    }],
    "fallback": {"type": "minecraft:model", "model": "gray_sun:item/starter_blade"}
  }
}
```

原版木劍保留原樣；只有帶自訂模型元件的物品使用此外觀：

```mcfunction
/give @s minecraft:wooden_sword[minecraft:item_model="gray_sun:starter_blade"] 1
```

## 此案例的姿勢分離

- GUI 模型：刀身所有元素以 `[8, 8, 8]` 為中心繞 Z 軸 `-45°`，`gui.rotation = [0,0,0]`，`gui.scale = [1.25,1.25,1.25]`。最終 GUI 幾何在手持修改期間保持一致。
- held 模型：以 GUI 模型複製後，只鏡射刀身元素的 X 範圍，`new_from_x = 16 - old_to_x`、`new_to_x = 16 - old_from_x`。握柄、纏繞、護手保持原坐標與旋轉。這讓亮色刃側由上側換到下側，且維持玩家原本較自然的握法。
- 第三人稱右手最後採用 `rotation: [0,-90,50]`、`translation: [0.5,4,0.5]`、`scale: [0.85,0.85,0.85]`；左手對應 `rotation: [0,90,-50]`、`translation: [-0.5,4,0.5]`。右手 Z 角從 55 改 50、X 位移從 0 改 0.5，是一次小幅抬刀並讓握柄更靠近手掌的調整。
- 第一人稱右手為 `rotation: [0,-90,25]`、`translation: [1.13,3.2,1.13]`、`scale: [0.68,0.68,0.68]`；本次最後的第三人稱微調未改第一人稱。
- 貼圖尺寸為 64×64；此範例把 Blockbench 的像素 UV 除以 4，得到 Java 模型的 0–16 UV。其他貼圖尺寸須重算。

這些顯示角度與位移並非通用預設。截圖比單看幾何角度更能揭露握點、透視和刃側問題；每次先保存使用者認可的視角，再單獨調整另一個情境。

範例保留 `gray_sun` namespace 作為案例識別；新專案使用自己的 namespace。兩個專案內嵌貼圖，亦提供 `starter_blade_palette.png`；若重新連結貼圖，選擇此 PNG。
