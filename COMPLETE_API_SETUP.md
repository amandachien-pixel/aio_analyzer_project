# 🔑 AIO 分析器完整 API 設定指引

## 📊 當前設定狀態檢查

### ❌ 需要設定的項目：
- [ ] Google Search Console API 憑證
- [ ] Google Ads API 配置  
- [ ] Serper API 金鑰
- [ ] 環境變數配置
- [ ] OAuth 授權完成

### ✅ 已就緒的項目：
- [x] 配置文件模板
- [x] 項目結構
- [x] 程式碼框架

---

## 🚀 第一步：Google Search Console API 設定

### 1.1 創建 Google Cloud 專案
1. 前往 [Google Cloud Console]()https://console.cloud.google.com/
2. 點擊「新建專案」
3. 專案名稱：`aio-analyzer-project`
4. 點擊「建立」

### 1.2 啟用 Search Console API
1. 在 Google Cloud Console 中，前往「API 和服務」→「程式庫」
2. 搜尋「Google Search Console API」
3. 點擊並啟用該 API

### 1.3 創建服務帳戶
1. 前往「API 和服務」→「憑證」
2. 點擊「建立憑證」→「服務帳戶」
3. 服務帳戶詳情：
   - 名稱：`aio-analyzer-service`
   - ID：`aio-analyzer-service`
   - 說明：`AIO Analyzer Search Console Access`

### 1.4 下載憑證並配置
```bash
# 下載 JSON 憑證文件後，執行：
cp ~/Downloads/your-service-account-key.json /Users/AmandaChien/aio_analyzer_project/config/credentials.json

# 檢查文件
ls -la /Users/AmandaChien/aio_analyzer_project/config/credentials.json
```

### 1.5 設定 Search Console 權限
1. 前往 [Google Search Console](https://search.google.com/search-console/)
2. 選擇您的網站屬性
3. 前往「設定」→「使用者和權限」
4. 新增使用者：使用 JSON 文件中的 `client_email`
5. 權限：「受限制」或「完整」

---

## 🎯 第二步：Google Ads API 設定

### 2.1 申請開發者權杖
1. 前往 [Google Ads API](https://developers.google.com/google-ads/api/docs/first-call/dev-token)
2. 使用有 Google Ads 帳戶的 Google 帳號登入
3. 申請開發者權杖（需 1-2 工作天審核）

### 2.2 創建 OAuth 憑證
1. 在同一個 Google Cloud 專案中，前往「憑證」
2. 點擊「建立憑證」→「OAuth 用戶端 ID」
3. 應用程式類型：「桌面應用程式」
4. 下載 JSON 檔案保存

### 2.3 獲取 Refresh Token
建立臨時腳本獲取 refresh token：

```python
# oauth_helper.py
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

def get_refresh_token():
    scopes = ['https://www.googleapis.com/auth/adwords']
    flow = InstalledAppFlow.from_client_secrets_file(
        'path/to/your/oauth_credentials.json', scopes)
    creds = flow.run_local_server(port=0)
    
    print(f"Client ID: {creds.client_id}")
    print(f"Client Secret: {creds.client_secret}")
    print(f"Refresh Token: {creds.refresh_token}")

if __name__ == '__main__':
    get_refresh_token()
```

### 2.4 創建 Google Ads 配置文件
```bash
cp /Users/AmandaChien/aio_analyzer_project/config/google-ads.yaml.template /Users/AmandaChien/aio_analyzer_project/config/google-ads.yaml
```

編輯 `google-ads.yaml`：
```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_OAUTH_CLIENT_ID"
client_secret: "YOUR_OAUTH_CLIENT_SECRET"  
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_MANAGER_ACCOUNT_ID"
customer_id: "YOUR_TARGET_CUSTOMER_ID"
```

---

## 🔍 第三步：Serper API 設定

### 3.1 註冊 Serper 帳戶
1. 前往 [Serper.dev](https://serper.dev/)
2. 點擊「Sign Up」註冊
3. 確認電子郵件

### 3.2 獲取 API 金鑰
1. 登入 Serper Dashboard
2. 前往「API Keys」
3. 複製 API 金鑰
4. 免費額度：2,500 查詢/月

### 3.3 測試 API 連接
```bash
curl -X POST 'https://google.serper.dev/search' \
  -H 'X-API-KEY: your-api-key-here' \
  -H 'Content-Type: application/json' \
  -d '{"q": "what is ai overview"}'
```

---

## ⚙️ 第四步：環境配置

### 4.1 創建 .env 文件
```bash
cp /Users/AmandaChien/aio_analyzer_project/config/env.example /Users/AmandaChien/aio_analyzer_project/.env
```

### 4.2 編輯 .env 文件
```bash
# AIO 分析器環境配置
# =====================

# Google Search Console API
GSC_CREDENTIALS_FILE=/Users/AmandaChien/aio_analyzer_project/config/credentials.json
GSC_TOKEN_FILE=/Users/AmandaChien/aio_analyzer_project/config/token.json

# Google Ads API
GOOGLE_ADS_YAML_FILE=/Users/AmandaChien/aio_analyzer_project/config/google-ads.yaml

# Serper API
SERP_API_PROVIDER=serper
SERP_API_KEY=your-serper-api-key-here
SERP_API_ENDPOINT=https://google.serper.dev/search

# 分析目標
SITE_URL=sc-domain:your-domain.com
CUSTOMER_ID=123-456-7890

# 效能設定
DEFAULT_RATE_LIMIT=10
MAX_CONCURRENT_REQUESTS=5
REPORTS_STORAGE_DAYS=30

# Django 設定（企業版）
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 資料庫設定
DB_NAME=aio_analyzer
DB_USER=postgres  
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis 設定
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

---

## 🧪 第五步：API 測試驗證

### 5.1 創建測試腳本
建立 `test_setup.py`：

```python
#!/usr/bin/env python3
import os
import sys
import asyncio
from pathlib import Path

# 添加專案路徑
sys.path.append(str(Path(__file__).parent / 'src'))

async def test_apis():
    """測試所有 API 連接"""
    
    print("🧪 開始 API 連接測試...")
    print("=" * 50)
    
    results = {
        'gsc': False,
        'ads': False, 
        'serp': False
    }
    
    # 測試 Google Search Console API
    print("📊 測試 Google Search Console API...")
    try:
        from config.settings import Config
        config = Config()
        
        # 檢查憑證文件
        cred_file = config.get('gsc.credentials_file')
        if os.path.exists(cred_file):
            print(f"✅ GSC 憑證文件存在: {cred_file}")
            results['gsc'] = True
        else:
            print(f"❌ GSC 憑證文件不存在: {cred_file}")
    except Exception as e:
        print(f"❌ GSC 配置錯誤: {e}")
    
    # 測試 Google Ads API
    print("🎯 測試 Google Ads API...")
    try:
        ads_file = config.get('ads.yaml_file')
        if os.path.exists(ads_file):
            print(f"✅ Google Ads 配置文件存在: {ads_file}")
            results['ads'] = True
        else:
            print(f"❌ Google Ads 配置文件不存在: {ads_file}")
    except Exception as e:
        print(f"❌ Google Ads 配置錯誤: {e}")
    
    # 測試 Serper API
    print("🔍 測試 Serper API...")
    try:
        api_key = config.get('serp.api_key')
        if api_key and api_key != "YOUR_SERP_API_KEY":
            print("✅ Serper API 金鑰已設定")
            
            # 實際測試 API 請求
            import aiohttp
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            data = {'q': 'test query'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://google.serper.dev/search',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        print("✅ Serper API 連接成功")
                        results['serp'] = True
                    else:
                        print(f"❌ Serper API 連接失敗: HTTP {response.status}")
        else:
            print("❌ Serper API 金鑰未設定")
    except Exception as e:
        print(f"❌ Serper API 測試失敗: {e}")
    
    # 總結
    print("=" * 50)
    success_count = sum(results.values())
    total_count = len(results)
    
    if success_count == total_count:
        print("🎉 所有 API 設定完成！")
        print("✅ 您可以開始使用 AIO 分析器了")
    else:
        print(f"⚠️  API 設定進度: {success_count}/{total_count}")
        print("❗ 請完成上述失敗項目的設定")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_apis())
```

### 5.2 執行測試
```bash
cd /Users/AmandaChien/aio_analyzer_project
python3 test_setup.py
```

---

## 🚀 第六步：啟動應用

### 6.1 本地預覽版（推薦開始）
```bash
cd /Users/AmandaChien/aio_analyzer_project/local_preview
python3 app.py
```
訪問：http://localhost:5001

### 6.2 企業版（完整功能）
```bash
cd /Users/AmandaChien/aio_analyzer_project/backend
python3 manage.py migrate
python3 manage.py runserver
```
訪問：http://localhost:8000

---

## 🛠️ 故障排除

### 常見問題與解決方案

#### Google Search Console API
- **403 錯誤**：服務帳戶未加入 Search Console 權限
- **檔案不存在**：檢查 credentials.json 路徑

#### Google Ads API  
- **開發者權杖問題**：等待 Google 審核
- **OAuth 錯誤**：重新執行授權流程

#### Serper API
- **401 錯誤**：檢查 API 金鑰是否正確
- **配額不足**：檢查使用量或升級方案

### 檢查清單
- [ ] Google Cloud 專案已建立
- [ ] Search Console API 已啟用  
- [ ] 服務帳戶憑證已下載
- [ ] Search Console 權限已設定
- [ ] Google Ads 開發者權杖已獲得
- [ ] OAuth 憑證已建立
- [ ] Refresh token 已獲取
- [ ] Serper 帳戶已註冊
- [ ] API 金鑰已取得
- [ ] credentials.json 已配置
- [ ] google-ads.yaml 已設定
- [ ] .env 文件已建立
- [ ] API 測試已通過

---

## 🎯 完成後的下一步

1. **測試分析流程**：執行完整的 AIO 分析
2. **優化參數**：調整速率限制和並發數
3. **監控使用量**：追蹤 API 配額消耗
4. **設定排程**：定期自動化分析

🎉 **恭喜！完成設定後，您就能使用真實數據進行 AIO 潛力分析了！**
