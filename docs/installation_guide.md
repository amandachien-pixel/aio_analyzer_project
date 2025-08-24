# 安裝與配置指南

本指南將詳細說明如何安裝和配置 AIO 潛力分析器。

## 系統需求

- Python 3.8 或更高版本
- 穩定的網絡連接
- Google Cloud 帳戶（用於 GSC 和 Ads API）
- SERP API 服務帳戶

## 安裝步驟

### 1. 下載項目

```bash
# 如果有 Git 倉庫
git clone https://github.com/your-repo/aio-analyzer.git
cd aio-analyzer

# 或者下載並解壓縮項目文件
```

### 2. 創建虛擬環境（推薦）

```bash
# 使用 venv
python -m venv aio_env
source aio_env/bin/activate  # Linux/Mac
# 或
aio_env\Scripts\activate     # Windows

# 使用 conda
conda create -n aio_env python=3.9
conda activate aio_env
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

如果遇到安裝問題，可以嘗試：

```bash
# 升級 pip
pip install --upgrade pip

# 逐個安裝核心依賴
pip install google-api-python-client
pip install google-ads
pip install pandas aiohttp
pip install tqdm colorlog
```

## API 配置

### Google Search Console API

#### 1. 創建 Google Cloud 項目

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新項目或選擇現有項目
3. 啟用 Google Search Console API

#### 2. 創建 OAuth 2.0 憑證

1. 在 Google Cloud Console 中，前往「API 和服務」>「憑證」
2. 點擊「創建憑證」>「OAuth 2.0 客戶端 ID」
3. 選擇「桌面應用程式」
4. 下載 JSON 憑證文件
5. 將文件重命名為 `credentials.json` 並放入 `config/` 目錄

#### 3. 設置 Search Console 權限

確保您的 Google 帳戶對目標網站具有 Search Console 的查看權限。

### Google Ads API

#### 1. 申請開發者令牌

1. 登入您的 [Google Ads 帳戶](https://ads.google.com/)
2. 前往「工具和設定」>「設定」>「API 中心」
3. 申請開發者令牌（Developer Token）
4. 等待審核通過（可能需要幾天時間）

#### 2. 配置 OAuth 2.0

1. 使用與 GSC 相同的 Google Cloud 項目
2. 確保已啟用 Google Ads API
3. 使用相同的 OAuth 2.0 憑證

#### 3. 創建配置文件

複製模板文件：

```bash
cp config/google-ads.yaml.template config/google-ads.yaml
```

編輯 `config/google-ads.yaml`：

```yaml
developer_token: "您的開發者令牌"
client_id: "您的OAuth客戶端ID.apps.googleusercontent.com"
client_secret: "您的OAuth客戶端密鑰"
refresh_token: "您的重新整理令牌"
login_customer_id: "管理員帳戶ID（如適用）"
customer_id: "目標客戶ID"
```

#### 4. 獲取重新整理令牌

使用 Google Ads API 的 OAuth 2.0 工具：

```bash
# 安裝 Google Ads API 工具
pip install google-ads

# 運行 OAuth 2.0 流程
python -m google.ads.googleads.oauth2.get_refresh_token \
    --client_id=您的客戶端ID \
    --client_secret=您的客戶端密鑰
```

### SERP API

#### 選項 1: SerpApi（推薦）

1. 前往 [SerpApi](https://serpapi.com/)
2. 註冊帳戶並獲取 API 金鑰
3. 選擇適合的定價方案

#### 選項 2: ScaleSerp

1. 前往 [ScaleSerp](https://scaleserp.com/)
2. 註冊並獲取 API 金鑰

#### 選項 3: 其他 SERP API 提供商

支援任何提供標準 REST API 的 SERP 服務。

## 環境配置

### 1. 創建環境變數文件

```bash
cp config/env.example .env
```

### 2. 編輯 .env 文件

```bash
# API 憑證
SERP_API_KEY=您的SERP_API金鑰

# 分析目標
SITE_URL=sc-domain:您的網站.com
CUSTOMER_ID=您的Google_Ads客戶ID

# 可選配置
LOG_LEVEL=INFO
OUTPUT_DIR=output
CONCURRENT_REQUESTS=10
```

### 3. 驗證配置

運行配置驗證腳本：

```python
from src.aio_analyzer import AIOAnalyzer

analyzer = AIOAnalyzer()
if analyzer.validate_configuration():
    print("✅ 配置驗證成功")
else:
    print("❌ 配置驗證失敗")
```

## 常見安裝問題

### 問題 1: Python 版本過舊

```bash
# 檢查 Python 版本
python --version

# 如果版本 < 3.8，請升級 Python
```

### 問題 2: 依賴安裝失敗

```bash
# 清理緩存
pip cache purge

# 使用國內鏡像源（中國用戶）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 問題 3: Google API 憑證問題

- 確保 JSON 憑證文件格式正確
- 檢查 OAuth 2.0 設定中的重新導向 URI
- 確認已啟用相關 API

### 問題 4: 權限錯誤

```bash
# 確保有足夠的文件系統權限
chmod 755 aio_analyzer_project/
chmod 644 config/*
```

## 安全建議

1. **不要提交憑證文件到版本控制**
   ```bash
   # 確保 .gitignore 包含：
   config/credentials.json
   config/google-ads.yaml
   .env
   ```

2. **定期輪換 API 金鑰**

3. **使用最小權限原則**
   - 只授予必要的 API 權限
   - 定期審查帳戶權限

4. **監控 API 使用量**
   - 設置使用量警報
   - 定期檢查計費狀況

## 驗證安裝

運行快速測試：

```bash
# 測試基本導入
python -c "from src.aio_analyzer import AIOAnalyzer; print('✅ 導入成功')"

# 運行簡單範例
python examples/basic_usage.py
```

如果所有測試通過，您就可以開始使用 AIO 潛力分析器了！

## 下一步

- 閱讀 [README.md](../README.md) 了解基本使用方法
- 查看 [examples/](../examples/) 目錄中的使用範例
- 運行您的第一次 AIO 分析
