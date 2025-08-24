# 🔑 Google APIs 獲取指南 - SiEtrendforce 專案

您的專案資訊：
- **專案名稱**: SiEtrendforce  
- **專案編號**: 21862818172
- **專案 ID**: sietrendforce

## 📋 第一步：Google Search Console API 設定

### 1️⃣ 前往 Google Cloud Console

1. 訪問：https://console.cloud.google.com/
2. 登入您的 Google 帳戶
3. 如果您已有專案，可以選擇現有的 "SiEtrendforce" 專案
4. 或者創建新專案：
   - 點擊頂部的專案選擇器
   - 點擊「新增專案」
   - 專案名稱：`AIO-Analyzer-SiEtrendforce`
   - 組織：選擇適當的組織（如果有）

### 2️⃣ 啟用 Search Console API

1. 在 Google Cloud Console 中，前往「API 和服務」→「程式庫」
2. 在搜尋框中輸入：`Google Search Console API`
3. 點擊「Google Search Console API」結果
4. 點擊「啟用」按鈕

### 3️⃣ 創建服務帳戶憑證

1. 前往「API 和服務」→「憑證」
2. 點擊「+ 建立憑證」
3. 選擇「服務帳戶」
4. 填寫服務帳戶詳細資料：
   ```
   服務帳戶名稱：aio-analyzer-service
   服務帳戶 ID：aio-analyzer-service  
   說明：AIO Analyzer for SiEtrendforce Search Console Access
   ```
5. 點擊「建立並繼續」
6. **角色部分**：可以跳過（選擇「繼續」）
7. **授予使用者存取權**：可以跳過（選擇「完成」）

### 4️⃣ 下載憑證 JSON 檔案

1. 在「憑證」頁面，找到剛建立的服務帳戶
2. 點擊服務帳戶的電子郵件地址
3. 切換到「金鑰」標籤
4. 點擊「新增金鑰」→「建立新金鑰」
5. 選擇「JSON」格式
6. 點擊「建立」
7. JSON 檔案會自動下載
8. **重要**：記住服務帳戶的電子郵件地址（類似：`aio-analyzer-service@your-project-id.iam.gserviceaccount.com`）

### 5️⃣ 在 Search Console 中添加服務帳戶權限

1. 前往：https://search.google.com/search-console/
2. 選擇您要分析的網站屬性（SiEtrendforce 相關網站）
3. 在左側選單中點擊「設定」
4. 點擊「使用者和權限」
5. 點擊「新增使用者」
6. 在「電子郵件地址」欄位中輸入服務帳戶的電子郵件地址
7. 選擇權限級別：
   - **受限制**：只能查看數據（推薦）
   - **完整**：可以查看和修改（如果需要）
8. 點擊「新增」

## 📊 第二步：Google Ads API 設定（可選）

### 1️⃣ 申請 Google Ads API 存取權限

1. 前往：https://developers.google.com/google-ads/api/docs/first-call/overview
2. 點擊「Get started」
3. 使用與您 Google Ads 帳戶關聯的 Google 帳號登入
4. 填寫 API 存取申請表單
5. 等待審核（通常 1-2 個工作天）

### 2️⃣ 創建 OAuth 2.0 憑證

1. 回到 Google Cloud Console
2. 前往「API 和服務」→「憑證」
3. 點擊「+ 建立憑證」
4. 選擇「OAuth 用戶端 ID」
5. 應用程式類型：選擇「桌面應用程式」
6. 名稱：`AIO Analyzer OAuth Client`
7. 點擊「建立」
8. 下載 OAuth JSON 檔案

### 3️⃣ 獲取開發者權杖

1. 前往：https://ads.google.com/nav/selectaccount?authuser=0&dst=/aw/apicenter
2. 登入您的 Google Ads 帳戶
3. 點擊「開始使用」或「API Center」
4. 申請開發者權杖（Developer Token）
5. 記錄您的客戶 ID

## 🛠️ 第三步：配置文件設定

### 將憑證檔案放置到正確位置

1. 將下載的 Search Console JSON 憑證檔案重新命名為 `credentials.json`
2. 將檔案移動到：`/Users/AmandaChien/aio_analyzer_project/config/credentials.json`

### 創建 Google Ads 配置檔案

創建檔案：`/Users/AmandaChien/aio_analyzer_project/config/google-ads.yaml`

```yaml
# Google Ads API 配置
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "YOUR_CUSTOMER_ID"
use_proto_plus: True
```

## 🧪 第四步：測試 API 連接

### 測試 Search Console API

```bash
# 確保您已設定 Serper API 金鑰
export SERP_API_KEY="71951a3f6dd85b7d264d81b9ad88c3eccb429355"

# 執行完整 API 測試
python3 test_apis.py
```

### 快速測試 GSC 連接

```python
# 建立快速測試腳本
python3 -c "
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 載入憑證
credentials = service_account.Credentials.from_service_account_file(
    'config/credentials.json',
    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)

# 建立服務
service = build('searchconsole', 'v1', credentials=credentials)

# 測試：取得網站列表
try:
    sites = service.sites().list().execute()
    print('✅ GSC API 連接成功！')
    print('可用網站：')
    for site in sites.get('siteEntry', []):
        print(f'  • {site[\"siteUrl\"]}')
except Exception as e:
    print(f'❌ GSC API 連接失敗: {e}')
"
```

## ⚡ 快速設定腳本

您也可以使用我們的自動化腳本：

```bash
# 1. 設定 Serper API（已完成）
export SERP_API_KEY="71951a3f6dd85b7d264d81b9ad88c3eccb429355"

# 2. 執行互動式設定助手
python3 setup_apis.py

# 3. 測試所有 API
python3 test_apis.py

# 4. 啟動應用
python3 local_preview/app_simple.py
```

## 🔍 故障排除

### 常見問題

**Q: 服務帳戶無法存取 Search Console 數據**
A: 確認您已在 Search Console 中添加服務帳戶的電子郵件地址

**Q: API 配額錯誤**
A: 檢查 Google Cloud Console 中的 API 配額限制

**Q: 憑證檔案格式錯誤**
A: 確認下載的是 JSON 格式，且包含所有必要欄位

### 檢查清單

- [ ] Google Cloud 專案已建立/選擇
- [ ] Search Console API 已啟用
- [ ] 服務帳戶已建立
- [ ] JSON 憑證已下載
- [ ] 服務帳戶已添加到 Search Console 權限
- [ ] 憑證檔案已放置在 `config/credentials.json`
- [ ] API 測試通過

## 📞 需要幫助？

如果遇到任何問題：

1. **檢查服務帳戶電子郵件**：確認已正確添加到 Search Console
2. **驗證憑證檔案**：確認 JSON 格式正確
3. **測試基本連接**：使用 `python3 test_apis.py`
4. **查看詳細錯誤**：檢查終端中的完整錯誤訊息

---

🎯 **下一步**：完成上述步驟後，您將擁有完整的 Google Search Console API 存取權限，可以開始分析 SiEtrendforce 的搜尋數據！
