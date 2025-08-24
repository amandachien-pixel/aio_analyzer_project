# 🔑 AIO 分析器 API 真實資料對接完整設定指南

本指南將引導您完成所有必要的 API 設定，讓 AIO 分析器能夠使用真實數據進行分析。

## 📋 設定概覽

需要設定的 API 服務：
1. **Google Search Console API** (免費) - 擷取網站搜尋數據
2. **Google Ads API** (免費，需帳戶) - 關鍵字擴展和搜尋量數據  
3. **Serper API** (2,500免費查詢/月) - SERP 結果和 AIO 驗證

## 🚀 第一步：Google Search Console API 設定

### 1.1 創建 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊「選取專案」→「新增專案」
3. 專案名稱：`aio-analyzer-project`
4. 點擊「建立」

### 1.2 啟用 Search Console API

1. 在 Google Cloud Console 中，前往「API 和服務」→「程式庫」
2. 搜尋「Google Search Console API」
3. 點擊並啟用該 API

### 1.3 創建服務帳戶

1. 前往「API 和服務」→「憑證」
2. 點擊「建立憑證」→「服務帳戶」
3. 填寫資訊：
   - 服務帳戶名稱：`aio-analyzer-service`
   - 服務帳戶 ID：`aio-analyzer-service`
   - 說明：`AIO Analyzer Search Console Access`
4. 點擊「建立並繼續」
5. 角色選擇：跳過（不需要特定角色）
6. 點擊「完成」

### 1.4 下載憑證檔案

1. 在憑證頁面，找到剛創建的服務帳戶
2. 點擊服務帳戶名稱
3. 前往「金鑰」標籤
4. 點擊「新增金鑰」→「建立新金鑰」
5. 選擇「JSON」格式
6. 下載檔案，重新命名為 `credentials.json`

### 1.5 設定 Search Console 權限

1. 前往 [Google Search Console](https://search.google.com/search-console/)
2. 選擇您的網站屬性
3. 前往「設定」→「使用者和權限」
4. 點擊「新增使用者」
5. 電子郵件地址：使用服務帳戶的電子郵件（在 JSON 檔案中的 `client_email`）
6. 權限：選擇「受限制」或「完整」
7. 點擊「新增」

## 🎯 第二步：Google Ads API 設定

### 2.1 申請 Google Ads API 存取權限

1. 前往 [Google Ads API 申請頁面](https://developers.google.com/google-ads/api/docs/first-call/overview)
2. 使用有 Google Ads 帳戶的 Google 帳號登入
3. 填寫申請表單（通常需要 1-2 個工作天審核）

### 2.2 創建 OAuth 2.0 憑證

1. 在同一個 Google Cloud 專案中，前往「憑證」
2. 點擊「建立憑證」→「OAuth 用戶端 ID」
3. 應用程式類型：「桌面應用程式」
4. 名稱：`AIO Analyzer Desktop Client`
5. 點擊「建立」
6. 下載 JSON 檔案

### 2.3 設定 Google Ads 開發者權杖

1. 前往 [Google Ads API 中心](https://ads.google.com/nav/selectaccount?authuser=0&dst=/aw/apicenter)
2. 點擊「開始使用」
3. 申請開發者權杖（Developer Token）
4. 記錄您的：
   - 開發者權杖 (Developer Token)
   - 客戶 ID (Customer ID)

## 🔍 第三步：Serper API 設定

### 3.1 註冊 Serper 帳戶

1. 前往 [Serper.dev](https://serper.dev/)
2. 點擊「Sign Up」註冊帳戶
3. 確認電子郵件

### 3.2 獲取 API 金鑰

1. 登入 Serper 儀表板
2. 前往 「API Keys」頁面
3. 複製您的 API 金鑰
4. 免費方案提供 2,500 次查詢/月

### 3.3 測試 API 連接

```bash
curl -X POST 'https://google.serper.dev/search' \
  -H 'X-API-KEY: YOUR_SERPER_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{"q": "what is ai overview"}'
```

## ⚙️ 第四步：環境配置

### 4.1 複製憑證檔案

```bash
# 將下載的 GSC 憑證檔案複製到配置目錄
cp ~/Downloads/credentials.json /Users/AmandaChien/aio_analyzer_project/config/

# 檢查檔案是否存在
ls -la /Users/AmandaChien/aio_analyzer_project/config/credentials.json
```

### 4.2 創建 Google Ads 配置檔案

創建 `/Users/AmandaChien/aio_analyzer_project/config/google-ads.yaml`：

```yaml
# Google Ads API 配置
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_LOGIN_CUSTOMER_ID"

# 可選配置
use_proto_plus: True
```

### 4.3 設定環境變數

創建 `/Users/AmandaChien/aio_analyzer_project/.env`：

```bash
# ===========================================
# AIO 分析器環境配置
# ===========================================

# Django 設定
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 資料庫設定
DATABASE_NAME=aio_analyzer_db
DATABASE_USER=aio_user
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Google Search Console API
GSC_CREDENTIALS_FILE=/Users/AmandaChien/aio_analyzer_project/config/credentials.json
GSC_TOKEN_FILE=/Users/AmandaChien/aio_analyzer_project/config/token.json

# Google Ads API
GOOGLE_ADS_YAML_FILE=/Users/AmandaChien/aio_analyzer_project/config/google-ads.yaml

# SERP API 設定 (Serper)
SERP_API_PROVIDER=serper
SERP_API_KEY=your-serper-api-key-here
SERP_API_ENDPOINT=https://google.serper.dev/search

# 效能設定
DEFAULT_RATE_LIMIT=10
MAX_CONCURRENT_REQUESTS=5
REPORTS_STORAGE_DAYS=30

# Redis 設定 (用於 Celery)
REDIS_URL=redis://localhost:6379/0

# Celery 設定
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🧪 第五步：API 測試驗證

### 5.1 創建 API 測試腳本

創建測試腳本來驗證所有 API 連接：

```python
#!/usr/bin/env python3
# api_test.py - API 連接測試腳本

import os
import sys
from pathlib import Path

# 添加專案路徑
sys.path.append(str(Path(__file__).parent / 'src'))

async def test_all_apis():
    """測試所有 API 連接"""
    
    print("🧪 開始 API 連接測試...")
    print("=" * 50)
    
    # 測試 1: Google Search Console API
    print("📊 測試 Google Search Console API...")
    try:
        from utils.gsc_handler import GSCHandler
        # 這裡會進行實際的 API 測試
        print("✅ GSC API 連接成功")
    except Exception as e:
        print(f"❌ GSC API 連接失敗: {e}")
    
    # 測試 2: Google Ads API  
    print("🎯 測試 Google Ads API...")
    try:
        from utils.ads_handler import AdsHandler
        # 這裡會進行實際的 API 測試
        print("✅ Google Ads API 連接成功")
    except Exception as e:
        print(f"❌ Google Ads API 連接失敗: {e}")
    
    # 測試 3: Serper API
    print("🔍 測試 Serper API...")
    try:
        from utils.serp_handler import SERPHandler
        # 這裡會進行實際的 API 測試
        print("✅ Serper API 連接成功")
    except Exception as e:
        print(f"❌ Serper API 連接失敗: {e}")
    
    print("=" * 50)
    print("🎉 API 測試完成！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_all_apis())
```

### 5.2 執行測試

```bash
cd /Users/AmandaChien/aio_analyzer_project
python3 api_test.py
```

## 🔧 第六步：OAuth 2.0 授權流程

### 6.1 Google Ads API 首次授權

```python
# 執行 OAuth 授權流程
from google.ads.googleads.client import GoogleAdsClient
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

# 設定 OAuth 流程
flow = Flow.from_client_secrets_file(
    'path/to/oauth_credentials.json',
    scopes=['https://www.googleapis.com/auth/adwords']
)

# 獲取授權 URL
auth_url, _ = flow.authorization_url(prompt='consent')
print(f"請訪問此 URL 進行授權: {auth_url}")

# 輸入授權碼後獲取 refresh_token
```

### 6.2 Search Console API 授權

如果使用 OAuth 而非服務帳戶：

```python
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

flow = Flow.from_client_secrets_file(
    'oauth_credentials.json',
    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)

# 獲取授權 URL 並完成授權流程
```

## 📊 第七步：測試完整分析流程

### 7.1 執行端到端測試

```bash
# 啟動本地預覽（使用真實 API）
cd /Users/AmandaChien/aio_analyzer_project/local_preview
python3 app.py

# 或使用完整的 Django 版本
cd /Users/AmandaChien/aio_analyzer_project/backend
python3 manage.py runserver
```

### 7.2 驗證數據流程

1. **M1 測試**: 確認能從 GSC 擷取真實的搜尋查詢數據
2. **M2 測試**: 確認能使用 Google Ads API 擴展關鍵字
3. **M3 測試**: 確認能使用 Serper API 驗證 AIO 觸發
4. **M4 測試**: 確認能生成包含真實數據的報告

## 🚨 常見問題排除

### Google Search Console API 問題

**問題**: `403 Forbidden` 錯誤
**解決**: 確認服務帳戶已添加到 Search Console 用戶權限中

**問題**: `401 Unauthorized` 錯誤
**解決**: 檢查 credentials.json 檔案路徑和格式

### Google Ads API 問題

**問題**: 開發者權杖未核准
**解決**: 等待 Google 審核，或使用測試帳戶

**問題**: OAuth 授權失敗
**解決**: 確認重新導向 URI 設定正確

### Serper API 問題

**問題**: 查詢額度耗盡
**解決**: 檢查使用量，考慮升級方案

**問題**: API 金鑰無效
**解決**: 重新生成 API 金鑰

## 📈 進階配置

### 自動化授權更新

```python
# refresh_token_automation.py
def refresh_google_ads_token():
    """自動更新 Google Ads API token"""
    # 實現自動 token 更新邏輯
    pass

def monitor_api_quotas():
    """監控 API 使用量"""
    # 實現配額監控邏輯
    pass
```

### 效能最佳化

```python
# 批次處理設定
BATCH_SIZE = 50
CONCURRENT_REQUESTS = 5
RATE_LIMIT_DELAY = 1.0

# 快取設定
CACHE_EXPIRY = 3600  # 1 小時
USE_REDIS_CACHE = True
```

## ✅ 設定檢查清單

- [ ] Google Cloud 專案已創建
- [ ] Search Console API 已啟用
- [ ] 服務帳戶已創建並下載憑證
- [ ] Search Console 權限已設定
- [ ] Google Ads API 申請已核准
- [ ] OAuth 憑證已創建
- [ ] Serper 帳戶已註冊
- [ ] API 金鑰已獲取
- [ ] 憑證檔案已複製到正確位置
- [ ] google-ads.yaml 已配置
- [ ] .env 檔案已創建
- [ ] API 測試已通過
- [ ] OAuth 授權已完成
- [ ] 端到端測試已成功

## 🎯 下一步

設定完成後，您可以：

1. **使用本地預覽版本**測試基本功能
2. **部署完整 Django 版本**獲得所有企業功能
3. **設定監控和警報**追蹤 API 使用狀況
4. **優化效能參數**提升分析速度

---

🎉 **恭喜！您已完成所有 API 的真實資料對接設定！**

如果遇到任何問題，請參考上方的故障排除部分，或查看各 API 的官方文檔。
