# Serper API 設定指南

本指南將協助您設定 Serper API 作為 AIO 分析器的 SERP 數據來源。

## 🌟 為什麼選擇 Serper？

### 💰 價格優勢
- **免費方案**: 2,500 次搜尋/月 (比 SerpApi 多 25 倍)
- **付費方案**: $50/月 100,000 次搜尋 (比 SerpApi 便宜 50%)
- **按量計費**: 更靈活的定價模式

### 🚀 技術優勢
- **高速 API**: 平均回應時間 < 1 秒
- **穩定性**: 99.9% 的正常運行時間
- **實時數據**: 即時的 Google 搜尋結果
- **全球支援**: 支援 100+ 國家和語言

## 📝 註冊步驟

### 1. 創建 Serper 帳戶

1. 前往 [Serper.dev](https://serper.dev/)
2. 點擊 "Get Started" 或 "Sign Up"
3. 使用 Google 帳戶或電子郵件註冊
4. 驗證您的電子郵件地址

### 2. 獲取 API 金鑰

1. 登入您的 Serper 控制台
2. 在 Dashboard 中找到 "API Key"
3. 複製您的 API 金鑰
4. 保存金鑰到安全位置

### 3. 選擇方案

| 方案 | 價格 | 搜尋次數/月 | 適用場景 |
|-----|------|------------|----------|
| **Free** | $0 | 2,500 | 測試和小型項目 |
| **Developer** | $50 | 100,000 | 中小企業 |
| **Startup** | $200 | 500,000 | 成長型企業 |
| **Pro** | $400 | 1,000,000 | 大型企業 |

## ⚙️ AIO 分析器配置

### 1. 更新環境變數

編輯您的 `.env` 文件：

```bash
# SERP API 設定 (使用 Serper)
SERP_API_PROVIDER=serper
SERP_API_KEY=your-serper-api-key-here
SERP_API_ENDPOINT=https://google.serper.dev/search

# 效能設定 (Serper 優化)
DEFAULT_RATE_LIMIT=20
MAX_CONCURRENT_REQUESTS=10
```

### 2. 驗證配置

在項目目錄中運行測試：

```bash
# 測試 Serper API 連接
python3 examples/test_serper.py
```

### 3. 優化設定

為了最佳效能，建議的配置：

```python
# 在 config/settings.py 中
SERP_CONFIG = {
    'provider': 'serper',
    'api_key': 'your-api-key',
    'endpoint': 'https://google.serper.dev/search',
    'country': 'tw',
    'language': 'zh-tw',
    'concurrent_requests': 10,  # Serper 支援更高並發
    'rate_limit': 2.0,          # 每秒 2 次請求
}
```

## 🔍 Serper vs SerpApi 比較

| 特性 | Serper | SerpApi |
|-----|--------|---------|
| **免費額度** | 2,500/月 | 100/月 |
| **入門價格** | $50/月 | $75/月 |
| **API 格式** | REST + JSON | REST + JSON |
| **回應速度** | < 1 秒 | 1-3 秒 |
| **全球位置** | ✅ | ✅ |
| **歷史數據** | ❌ | ✅ |
| **圖片搜尋** | ✅ | ✅ |
| **新聞搜尋** | ✅ | ✅ |

## 🛠️ 進階配置

### 自定義請求參數

```python
# 在分析任務中自定義 Serper 參數
serper_params = {
    'q': 'your search query',
    'gl': 'tw',           # 台灣
    'hl': 'zh-tw',        # 繁體中文
    'num': 10,            # 結果數量
    'start': 0,           # 起始位置
    'tbs': 'qdr:w',       # 時間範圍: 一週內
    'type': 'search',     # 搜尋類型
}
```

### 錯誤處理和重試

```python
# Serper API 錯誤碼處理
ERROR_CODES = {
    400: "請求格式錯誤",
    401: "API 金鑰無效",
    429: "請求頻率過高",
    500: "伺服器錯誤",
}
```

### 監控使用量

1. 在 Serper 控制台查看使用統計
2. 設定使用量警報
3. 監控 API 回應時間
4. 追蹤成本效益

## 🚨 注意事項

### 使用限制
- **每秒請求數**: 最多 10 個並發請求
- **請求大小**: 最大 8KB
- **回應大小**: 最大 1MB
- **超時時間**: 30 秒

### 最佳實踐
1. **快取結果**: 避免重複查詢相同關鍵字
2. **批次處理**: 合理安排查詢時間間隔
3. **錯誤重試**: 實作指數退避重試機制
4. **監控配額**: 定期檢查 API 使用量

### 疑難排解

#### 常見錯誤

**401 Unauthorized**
```bash
# 檢查 API 金鑰
curl -X POST https://google.serper.dev/search \
  -H 'X-API-KEY: your-api-key' \
  -H 'Content-Type: application/json' \
  -d '{"q": "test"}'
```

**429 Too Many Requests**
```python
# 降低請求頻率
SERP_CONFIG = {
    'rate_limit': 0.5,  # 每 2 秒一次請求
    'concurrent_requests': 3  # 降低並發數
}
```

## 📞 支援資源

- **Serper 文檔**: [https://serper.dev/docs](https://serper.dev/docs)
- **API 參考**: [https://serper.dev/api](https://serper.dev/api)
- **技術支援**: support@serper.dev
- **狀態頁面**: [https://status.serper.dev](https://status.serper.dev)

## ✅ 設定檢查清單

- [ ] 註冊 Serper 帳戶
- [ ] 獲取 API 金鑰
- [ ] 選擇適合的方案
- [ ] 更新 `.env` 配置文件
- [ ] 測試 API 連接
- [ ] 設定使用量監控
- [ ] 配置錯誤處理
- [ ] 執行首次 AIO 分析

完成以上步驟後，您就可以使用 Serper API 進行 AIO 潛力分析了！🎉
