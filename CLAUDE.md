# skill-conflict-checker 開發準則

## 模型限制

- 分析用模型最高 `claude-sonnet-4-6`，**嚴禁使用 opus**
- CLI 預設模型：`claude-haiku-4-5-20251001`（日常）
- 需要更深入分析時：`--model claude-sonnet-4-6`

## 開發規範

- 遵循 SOLID 原則，新 collector/reporter/analyzer 各自獨立一個檔案
- 測試覆蓋：每個新 collector 必須有對應單元測試
- secret 遮罩：任何含有 env 的來源都必須通過 `_mask_env` 處理
