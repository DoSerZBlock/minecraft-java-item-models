# Minecraft Java Item Models

A reusable Codex skill for creating and refining Blockbench item models and Minecraft Java resource packs. Instructions are written in Traditional Chinese.

可重複使用的 Minecraft Java 物品建模 skill，適用於武器、工具及道具，包含任務合約、顯示校準、結構對稱檢查、GUI 光照與資源包交付流程。

## 安裝到 Codex

在 Codex 輸入：

```text
$skill-installer 請從 https://github.com/wagcies444/minecraft-java-item-models 安裝 skills/minecraft-java-item-models
```

或下載此 repo，將整個 `skills/minecraft-java-item-models` 資料夾放到專案的 `.agents/skills/`，或個人目錄的 `~/.agents/skills/`。保留資料夾內所有相依檔案。安裝後若尚未顯示，重新啟動 Codex。[官方 skill 安裝與目錄說明](https://learn.chatgpt.com/docs/build-skills)

## 使用

```text
$minecraft-java-item-models
幫我製作 Minecraft Java 26.2 的短劍，使用 32×32 貼圖。
先建立 task.toml 與 Pass A blockout，提供可編輯 bbmodel、PNG 和資源包。
以第一人稱右手為主要視角，GUI 必須能清楚辨識輪廓。
```

修改現有物品時，提供目前的 `.bbmodel`、貼圖、目標版本和要調整的視角；已有遊戲截圖時一併提供，讓 skill 保留已通過的姿勢。

需求：能讀寫檔案的 Codex、Python 3.11+（任務驗證器只用標準庫）。Blockbench 用於專案檢查、編輯與預覽；Minecraft Java 用於實際遊戲驗收。此 skill 本身不安裝軟體或提供遊戲控制工具。

## 隨附內容

- [SKILL.md](skills/minecraft-java-item-models/SKILL.md)：完整操作流程。
- [施工規範](skills/minecraft-java-item-models/references/AI_MODELING_SPEC.md)與[顯示校準](skills/minecraft-java-item-models/references/DISPLAY_CALIBRATION.md)：規格優先、輪廓先行、rotation → translation → scale。
- [任務模板](skills/minecraft-java-item-models/assets/templates/MODEL_TASK.template.toml)、[缺陷模板](skills/minecraft-java-item-models/assets/templates/DISPLAY_DEFECTS.template.md)與 [TOML 驗證器](skills/minecraft-java-item-models/scripts/validate_task.py)。
- [範例資產](skills/minecraft-java-item-models/assets/example/)：兩個可編輯短刃專案、64×64 貼圖與 Java 26.2 資源包。
- [26.2 歷史案例](skills/minecraft-java-item-models/references/gray-sun-26.2.md)：GUI／held 分支及姿勢校準；範例數值須按新模型重新評估。

從 repo 根目錄執行模板結構驗證：

```sh
python skills/minecraft-java-item-models/scripts/validate_task.py skills/minecraft-java-item-models/assets/templates/MODEL_TASK.template.toml
```

模板仍含 `replace_me`、版本和執行環境的示例值，使用前須填寫。驗證器的 PASS 只代表它涵蓋的 TOML 欄位與預算檢查通過；它不檢查輸出是否存在、旋轉後 bounds、Java 旋轉限制、display policy 或視覺品質。

## 範例與驗證範圍

短刃範例來自作者的灰日建模工作區，`gray_sun` 是範例 namespace。新專案使用自己的名稱與設計；這份 skill 不要求採用該世界觀。

原案例曾以使用者遊戲截圖迭代。本次公開整理檢查了 skill 格式、TOML、JSON、ZIP、檔案相依、模型／貼圖／UV 的靜態一致性；未重新執行 Blockbench、渲染或遊戲測試。範例保留原專案 metadata；版本相容性與原生 GUI 光照仍須在目標 Blockbench 版本內確認。

資源包針對 Java 26.2，對應 resource pack 88.0；其他版本須重新查閱 [Mojang 的版本說明](https://feedback.minecraft.net/hc/en-us/articles/46690753273997-Minecraft-Java-Edition-26-2)。

## 授權

本 repo 的 skill、腳本、文件與隨附範例採用 [MIT License](LICENSE)，允許使用、修改及再散布，請保留授權與版權聲明。連結到的外部文件與第三方參考作品保留各自權利。此專案與 Mojang、Microsoft、Blockbench 或 OpenAI 沒有隸屬關係。
