# 🤖 AIO 潛力分析器 (AI Overview Potential Analyzer)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![GitHub Stars](https://img.shields.io/github/stars/amandachien-pixel/aio_analyzer_project?style=social)

**一個專業的 SEO 工具，用於分析關鍵字觸發 Google AI Overview (AIO) 的潛力。**

透過整合 Google Search Console、Google Ads API 和 SERP API，提供全面的 AIO 分析報告，幫助 SEO 專家和數位行銷人員在 AI 時代保持競爭優勢。

## 🌟 為什麼選擇 AIO 分析器？

- 🎯 **精準分析**: 程式化驗證關鍵字是否觸發 AI Overview
- 📊 **數據整合**: 整合多個 Google API 和 SERP API
- ⚡ **高效處理**: 異步處理，支援大規模關鍵字分析
- 📱 **易於使用**: 提供 Web 界面和命令行工具
- 🔒 **企業級**: 支援 Docker 部署和多用戶管理

## 🌟 主要功能

- **📊 數據整合**: 從多個 Google API 和第三方 SERP API 擷取數據
- **🔍 關鍵字擴展**: 使用 Google Ads API 從種子關鍵字生成相關建議
- **🤖 AIO 驗證**: 程式化驗證關鍵字是否觸發 Google AI Overview
- **📈 效能監控**: 異步處理和速率限制，確保高效執行
- **📋 綜合報告**: 生成多格式報告，包含統計分析和視覺圖表

## 🏗️ 項目結構

```
aio_analyzer_project/
├── src/
│   ├── aio_analyzer.py         # 主要分析器
│   └── utils/                  # 工具模組
│       ├── __init__.py
│       ├── gsc_handler.py      # Google Search Console 處理器
│       ├── ads_handler.py      # Google Ads API 處理器
│       ├── serp_handler.py     # SERP API 處理器
│       ├── report_generator.py # 報告生成器
│       └── logger.py           # 日誌管理
├── config/                     # 配置文件
│   ├── __init__.py
│   ├── settings.py             # 主要配置
│   ├── credentials.json.template
│   ├── google-ads.yaml.template
│   └── env.example
├── docs/                       # 文檔
├── examples/                   # 使用範例
├── tests/                      # 測試文件
├── output/                     # 輸出報告（自動創建）
├── logs/                       # 日誌文件（自動創建）
├── requirements.txt            # 依賴套件
└── README.md                   # 本文件
```

## 🚀 快速開始

### 1. 克隆項目

```bash
# 克隆 GitHub 倉庫
git clone https://github.com/amandachien-pixel/aio_analyzer_project.git
cd aio_analyzer_project

# 安裝依賴
pip install -r requirements.txt
```

### 2. 快速體驗（演示模式）

```bash
# 立即體驗所有功能（無需 API 憑證）
python3 local_preview/app_simple.py

# 訪問: http://localhost:5001
```

### 3. 使用真實數據

參考 [API 設定指南](API_SETUP_GUIDE.md) 配置：
- Google Search Console API
- Google Ads API  
- Serper API

### 2. 配置設置

#### 2.1 Google Search Console API
1. 在 [Google Cloud Console](https://console.cloud.google.com/) 創建項目
2. 啟用 Google Search Console API
3. 創建 OAuth 2.0 憑證並下載 JSON 文件
4. 將憑證文件重命名為 `credentials.json` 並放入 `config/` 目錄

#### 2.2 Google Ads API
1. 申請 [Google Ads API 開發者令牌](https://developers.google.com/google-ads/api/docs/first-call/dev-token)
2. 複製 `config/google-ads.yaml.template` 為 `config/google-ads.yaml`
3. 填入您的 API 憑證信息

#### 2.3 SERP API
1. 註冊 [SerpApi](https://serpapi.com/) 或其他 SERP API 提供商
2. 複製 `config/env.example` 為 `.env`
3. 填入您的 API 金鑰

### 3. 配置檔案設定

編輯 `config/settings.py` 中的分析目標：

```python
"analysis": {
    "site_url": "sc-domain:your-domain.com",  # 您的網站 GSC 屬性
    "customer_id": "123-456-7890",            # Google Ads 客戶 ID
    # ... 其他設定
}
```

### 4. 執行分析

```bash
# 執行完整 AIO 潛力分析
python src/aio_analyzer.py
```

## 📖 詳細使用說明

### 基本使用

```python
from src.aio_analyzer import AIOAnalyzer

# 初始化分析器
analyzer = AIOAnalyzer()

# 執行完整分析
results = await analyzer.run_full_analysis(
    days_back=90,  # 分析過去 90 天的數據
    regex_pattern=r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b'
)

print(f"分析結果: {results}")
```

### 分步驟執行

```python
# 1. 提取種子關鍵字
gsc_data = await analyzer.extract_seed_keywords(
    start_date=datetime.now() - timedelta(days=90),
    end_date=datetime.now(),
    regex_pattern=r'^(what|how|why)\b'
)

# 2. 擴展關鍵字
expanded_data = await analyzer.expand_keywords(
    seed_keywords=gsc_data['query'].tolist()
)

# 3. 驗證 AIO 觸發
validated_data = await analyzer.validate_aio_triggers(expanded_data)

# 4. 生成報告
report_path = await analyzer.generate_comprehensive_report(
    final_df=validated_data,
    gsc_df=gsc_data
)
```

## 📊 報告輸出

分析完成後，系統會在 `output/` 目錄生成以下報告：

- **主報告** (`aio_analysis_report_YYYYMMDD_HHMMSS.csv`): 完整的關鍵字分析結果
- **摘要報告** (`aio_summary_YYYYMMDD_HHMMSS.json`): JSON 格式的分析摘要
- **統計報告** (`aio_statistics_YYYYMMDD_HHMMSS.txt`): 詳細統計信息
- **視覺圖表** (如果啟用): AIO 分布圖、搜尋量分布等
- **元數據** (`report_metadata_YYYYMMDD_HHMMSS.json`): 報告相關信息

### 報告欄位說明

| 欄位名稱 | 說明 |
|---------|------|
| 目標關鍵字 | 分析的關鍵字 |
| 每月搜尋量 | Google Ads API 提供的平均月搜尋量 |
| 競爭程度 | 關鍵字的競爭程度 (LOW/MEDIUM/HIGH) |
| 觸發AIO | 是否觸發 Google AI Overview (Y/N) |
| 競爭指數 | 數值化的競爭指數 (0-100) |
| 最低出價(USD) | 預估的最低出價 |
| 最高出價(USD) | 預估的最高出價 |

## ⚙️ 配置選項

### 主要配置參數

```python
# 在 config/settings.py 中
CONFIG = {
    "serp": {
        "concurrent_requests": 10,  # 並發請求數
        "rate_limit": 1.0,         # 每秒請求率
        "timeout": 30              # 請求超時時間
    },
    "performance": {
        "retry_attempts": 3,       # 重試次數
        "chunk_size": 100         # 批次處理大小
    },
    "output": {
        "format": "csv",          # 輸出格式: csv, excel, json
        "include_charts": True    # 是否生成圖表
    }
}
```

### 環境變數

您也可以通過環境變數覆蓋配置：

```bash
export SERP_API_KEY="your_api_key"
export SITE_URL="sc-domain:your-domain.com"
export CUSTOMER_ID="123-456-7890"
export LOG_LEVEL="DEBUG"
```

## 🔧 進階功能

### 自定義正則表達式

針對不同類型的關鍵字使用不同的篩選條件：

```python
# 問句型關鍵字
question_regex = r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b'

# 商業意圖關鍵字
commercial_regex = r'(buy|purchase|price|cost|cheap|best|review|比較|購買|價格)\b'

# 品牌相關關鍵字
brand_regex = r'(brand_name|competitor_name)\b'
```

### 批次處理多個網站

```python
sites = [
    "sc-domain:site1.com",
    "sc-domain:site2.com",
    "sc-domain:site3.com"
]

for site in sites:
    analyzer.config.set('analysis.site_url', site)
    results = await analyzer.run_full_analysis()
    print(f"網站 {site} 分析完成")
```

## 🐛 常見問題

### Q: 出現 "找不到 GSC 憑證文件" 錯誤
A: 確保已從 Google Cloud Console 下載 OAuth 2.0 憑證 JSON 文件，並正確放置在 `config/credentials.json`

### Q: Google Ads API 請求失敗
A: 檢查以下項目：
- 開發者令牌是否有效
- 客戶 ID 格式是否正確（可包含或不包含連字號）
- 是否有權限訪問指定的客戶帳戶

### Q: SERP API 速率限制
A: 調整 `config/settings.py` 中的速率限制設定：
```python
"serp": {
    "rate_limit": 0.5,  # 降低每秒請求數
    "concurrent_requests": 5  # 減少並發數
}
```

### Q: 分析結果為空
A: 可能的原因：
- GSC 權限不足或網站未驗證
- 正則表達式過於嚴格，沒有匹配到關鍵字
- 時間範圍內沒有足夠的數據

## 📈 效能優化

### 建議設定

對於大量關鍵字分析：

```python
# 在 config/settings.py 中優化設定
"serp": {
    "concurrent_requests": 20,    # 提高並發數
    "rate_limit": 2.0            # 提高請求頻率
},
"performance": {
    "chunk_size": 200,           # 增大批次大小
    "timeout": 60                # 延長超時時間
}
```

### 監控與日誌

啟用詳細日誌以監控執行狀況：

```python
"logging": {
    "level": "DEBUG",            # 詳細日誌
    "file": "logs/debug.log"     # 日誌文件
}
```

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設置

```bash
# 安裝開發依賴
pip install -r requirements.txt

# 運行測試
python -m pytest tests/

# 代碼格式化
black src/
flake8 src/
```

## 📄 許可證

本項目採用 MIT 許可證 - 詳見 [LICENSE](LICENSE) 文件。

## 🆘 支援

如需技術支援或有任何疑問：

1. 查看本文檔的常見問題部分
2. 搜尋現有的 [Issues](https://github.com/your-repo/issues)
3. 創建新的 Issue 描述您的問題

## 📝 更新日誌

### v1.0.0 (2024-08-18)
- ✨ 初始版本發布
- 🚀 支援 GSC、Google Ads API 和 SERP API 整合
- 📊 完整的報告生成功能
- ⚡ 異步處理和效能優化
- 📖 完整的文檔和使用指南

## 🌟 演示和截圖

### 本地預覽界面
![AIO 分析器界面](https://via.placeholder.com/800x400/667eea/ffffff?text=AIO+%E5%88%86%E6%9E%90%E5%99%A8+%E7%95%8C%E9%9D%A2)

### 分析報告範例
![分析報告](https://via.placeholder.com/800x300/764ba2/ffffff?text=%E5%88%86%E6%9E%90%E5%A0%B1%E5%91%8A%E7%AF%84%E4%BE%8B)

## 🤝 貢獻指南

歡迎貢獻代碼、報告問題或提出功能建議！

### 如何貢獻
1. Fork 這個倉庫
2. 創建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

### 報告問題
如果您發現 bug 或有功能建議，請在 [Issues](https://github.com/amandachien-pixel/aio_analyzer_project/issues) 中報告。

## ⭐ 如果這個項目對您有幫助，請給我們一個 Star！

## 📞 聯繫方式

- **GitHub Issues**: [報告問題或建議](https://github.com/amandachien-pixel/aio_analyzer_project/issues)
- **討論**: [GitHub Discussions](https://github.com/amandachien-pixel/aio_analyzer_project/discussions)

---

**注意**: 本工具僅供研究和分析使用，請遵守各 API 提供商的使用條款和速率限制。
