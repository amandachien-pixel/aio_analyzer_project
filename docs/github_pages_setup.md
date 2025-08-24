# 🚀 GitHub Pages 免費測試網站設定指南

## 📋 概述

GitHub Pages 是完全免費的靜態網站託管服務，非常適合用來測試 Google Search Console API。設定過程只需要 10-15 分鐘！

## 🎯 完成後您將擁有：
- ✅ 免費的 `https://yourusername.github.io/aio-test` 網站
- ✅ 可以添加到 Google Search Console 的網站
- ✅ 完整的 AIO 分析器 API 測試環境

---

## 🔧 步驟一：註冊 GitHub 帳戶

### 1.1 前往 GitHub
1. 訪問：**https://github.com**
2. 點擊右上角 **「Sign up」**

### 1.2 創建帳戶
```
用戶名：選擇一個好記的名稱（例如：sietrendforce-test）
電子郵件：您的電子郵件地址
密碼：安全的密碼
```

### 1.3 完成驗證
1. 驗證電子郵件地址
2. 完成人機驗證（如果需要）
3. 選擇免費方案（Free plan）

---

## 📁 步驟二：創建新 Repository

### 2.1 創建 Repository
1. 登入 GitHub 後，點擊右上角 **「+」** → **「New repository」**
2. 填寫 Repository 資訊：
```
Repository name: aio-test-site
Description: AIO Analyzer Test Website for Search Console
Public: ✅ 選擇 Public（必須是公開才能使用 GitHub Pages）
Add a README file: ✅ 勾選
```
3. 點擊 **「Create repository」**

### 2.2 啟用 GitHub Pages
1. 在新建的 repository 中，點擊 **「Settings」** 標籤
2. 在左側選單中找到 **「Pages」**
3. 在 **「Source」** 部分：
   - 選擇 **「Deploy from a branch」**
   - Branch: 選擇 **「main」**
   - Folder: 選擇 **「/ (root)」**
4. 點擊 **「Save」**

### 2.3 獲取網站 URL
- GitHub 會顯示您的網站 URL：`https://yourusername.github.io/aio-test-site`
- 網站通常在 5-10 分鐘內生效

---

## 🌐 步驟三：創建測試網站內容

### 3.1 創建 index.html
1. 在 repository 主頁面，點擊 **「Add file」** → **「Create new file」**
2. 檔案名稱輸入：`index.html`
3. 複製以下內容：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AIO 分析器測試網站，用於 Google Search Console API 測試">
    <meta name="keywords" content="AIO,AI Overview,SEO,分析器,搜尋引擎優化">
    <title>AIO 分析器測試網站 | SiEtrendforce</title>
    
    <!-- Google Search Console 驗證標籤會在這裡添加 -->
    
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 { color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        h2 { color: #764ba2; margin-top: 30px; }
        .highlight { background: #f8f9ff; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }
        .keywords { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }
        footer { text-align: center; margin-top: 40px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 AIO 分析器測試網站</h1>
            <p><strong>專案：</strong>SiEtrendforce | <strong>用途：</strong>Google Search Console API 測試</p>
        </header>

        <main>
            <section>
                <h2>🎯 什麼是 AI Overview？</h2>
                <div class="highlight">
                    <p>AI Overview 是 Google 搜尋結果中由人工智慧生成的概述內容，幫助用戶快速理解複雜主題。這項功能正在改變 SEO 策略的制定方式。</p>
                </div>
                
                <div class="keywords">
                    <strong>相關關鍵字：</strong>什麼是 AI Overview, how to optimize for AI overview, AI overview SEO strategy
                </div>
            </section>

            <section>
                <h2>🔍 如何優化 AI Overview？</h2>
                <ul>
                    <li>創建高質量、結構化的內容</li>
                    <li>使用清晰的標題和子標題</li>
                    <li>提供準確、權威的資訊</li>
                    <li>優化Featured Snippets</li>
                    <li>關注語義搜尋和自然語言</li>
                </ul>
                
                <div class="keywords">
                    <strong>相關關鍵字：</strong>AI overview optimization, best practices for AI overview, AI overview ranking factors
                </div>
            </section>

            <section>
                <h2>📊 AIO 分析器功能</h2>
                <div class="highlight">
                    <p>AIO 分析器是一個強大的工具，可以：</p>
                    <ul>
                        <li>從 Google Search Console 擷取搜尋數據</li>
                        <li>使用 Google Ads API 擴展關鍵字</li>
                        <li>通過 SERP API 驗證 AI Overview 觸發</li>
                        <li>生成詳細的分析報告</li>
                    </ul>
                </div>
                
                <div class="keywords">
                    <strong>相關關鍵字：</strong>AIO analyzer tool, AI overview detection, SERP analysis, keyword research
                </div>
            </section>

            <section>
                <h2>🚀 開始使用</h2>
                <p>要開始使用 AIO 分析器：</p>
                <ol>
                    <li>設定 Google Search Console API</li>
                    <li>配置 Serper API 金鑰</li>
                    <li>運行分析並下載報告</li>
                </ol>
                
                <div class="keywords">
                    <strong>相關關鍵字：</strong>how to use AIO analyzer, Google Search Console setup, API configuration guide
                </div>
            </section>
        </main>

        <footer>
            <p>&copy; 2024 AIO 分析器測試網站 | 由 SiEtrendforce 提供 | 用於 API 測試目的</p>
            <p><small>本網站專門用於測試 Google Search Console API 和 AI Overview 分析功能</small></p>
        </footer>
    </div>

    <!-- 結構化數據 -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "AIO 分析器測試網站",
        "description": "專門用於測試 Google Search Console API 和 AI Overview 分析功能的網站",
        "url": "https://yourusername.github.io/aio-test-site",
        "author": {
            "@type": "Organization",
            "name": "SiEtrendforce"
        }
    }
    </script>
</body>
</html>
```

4. 在底部添加提交訊息：`Add AIO analyzer test website`
5. 點擊 **「Commit new file」**

### 3.2 等待網站生效
- 通常需要 5-10 分鐘
- 訪問您的網站：`https://yourusername.github.io/aio-test-site`
- 確認網站正常顯示

---

## 🔧 步驟四：添加到 Google Search Console

### 4.1 前往 Search Console
1. 訪問：**https://search.google.com/search-console/**
2. 點擊 **「新增屬性」**

### 4.2 選擇屬性類型
1. 選擇 **「URL 前置字元」**
2. 輸入您的完整網站 URL：
```
https://yourusername.github.io/aio-test-site
```
3. 點擊 **「繼續」**

### 4.3 驗證所有權 - HTML 標籤方法（推薦）
1. Google 會提供一個 meta 標籤，類似：
```html
<meta name="google-site-verification" content="abcd1234..." />
```

2. 複製這個標籤

3. 回到 GitHub，編輯 `index.html` 檔案：
   - 點擊檔案名稱 `index.html`
   - 點擊鉛筆圖示（編輯）
   - 在 `<head>` 區段中找到這行：
   ```html
   <!-- Google Search Console 驗證標籤會在這裡添加 -->
   ```
   - 將其替換為您的驗證標籤

4. 提交變更：
   - 提交訊息：`Add Google Search Console verification`
   - 點擊 **「Commit changes」**

5. 等待 2-3 分鐘讓變更生效

6. 回到 Search Console 點擊 **「驗證」**

### 4.4 驗證成功
✅ 如果一切順利，您會看到「驗證成功」的訊息！

---

## 🎯 步驟五：設定服務帳戶權限

### 5.1 創建服務帳戶（如前所述）
1. 前往 Google Cloud Console
2. 創建服務帳戶並下載 JSON 憑證
3. 記錄服務帳戶電子郵件地址

### 5.2 在 Search Console 中添加權限
1. 在 Search Console 中選擇您的新網站
2. 左側選單：**「設定」** → **「使用者和權限」**
3. 點擊 **「新增使用者」**
4. 輸入服務帳戶的電子郵件地址
5. 權限選擇：**「受限制」**
6. 點擊 **「新增」**

---

## 🧪 步驟六：測試 API 連接

### 6.1 將憑證檔案放到正確位置
```bash
# 將下載的 JSON 憑證重新命名並移動
mv ~/Downloads/your-service-account-key.json /Users/AmandaChien/aio_analyzer_project/config/credentials.json
```

### 6.2 測試 GSC API 連接
```bash
cd /Users/AmandaChien/aio_analyzer_project
python3 test_apis.py
```

### 6.3 如果測試成功，啟動完整版
```bash
# 設定所有 API 金鑰
export SERP_API_KEY="71951a3f6dd85b7d264d81b9ad88c3eccb429355"

# 啟動完整版本（使用真實 GSC 數據）
python3 local_preview/app.py
```

---

## 📈 步驟七：開始真實分析

現在您可以使用真實的 GSC 數據進行分析：

1. **輸入網站 URL**：`https://yourusername.github.io/aio-test-site`
2. **選擇日期範圍**：最近 30 天
3. **設定關鍵字篩選**：問句型關鍵字
4. **開始分析**：獲得真實的搜尋數據 + AIO 檢測結果

---

## 🎉 完成檢查清單

- [ ] GitHub 帳戶已創建
- [ ] Repository 已建立並啟用 Pages
- [ ] 測試網站已上線
- [ ] 網站已添加到 Search Console
- [ ] HTML 標籤驗證已完成
- [ ] 服務帳戶已創建
- [ ] 服務帳戶權限已設定
- [ ] API 測試已通過
- [ ] AIO 分析器正常運作

---

## 💡 額外技巧

### 提升網站 SEO 效果
1. **添加更多頁面**：創建 `about.html`, `blog.html` 等
2. **提交 Sitemap**：使用 GitHub Actions 自動生成
3. **等待索引**：通常需要 1-2 週才會有搜尋數據

### 模擬真實使用情境
```html
<!-- 添加更多測試關鍵字頁面 -->
<h2>什麼是機器學習？</h2>
<h2>如何學習 SEO？</h2>
<h2>最佳的 AI 工具推薦</h2>
```

### 監控網站效能
- 使用 Google Analytics（可選）
- 定期檢查 Search Console 數據
- 觀察 AIO 觸發率變化

---

## 🚀 **現在您就有了完整的測試環境！**

完成後，您將擁有：
- ✅ **免費的測試網站**
- ✅ **真實的 GSC API 連接**  
- ✅ **完整的 AIO 分析功能**
- ✅ **可以分析真實搜尋數據**

**準備好創建您的免費測試網站了嗎？** 🎯
