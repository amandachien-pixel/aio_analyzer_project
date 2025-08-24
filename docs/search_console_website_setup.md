# 🌐 Google Search Console 網站設定指南

## 📋 情況說明

如果您在 Google Search Console 中沒有網站屬性，需要先添加和驗證網站才能使用 API。

## 🔧 方案一：添加 SiEtrendforce 網站到 Search Console

### 第一步：前往 Google Search Console

1. 訪問：**https://search.google.com/search-console/**
2. 登入您的 Google 帳戶
3. 如果是第一次使用，會看到「開始使用」頁面

### 第二步：添加網站屬性

#### 選項 A：網域屬性（推薦）
```
類型：網域
網域：sietrendforce.com  # 您的實際網域
```

#### 選項 B：URL 前置字元
```
類型：URL 前置字元  
URL：https://www.sietrendforce.com  # 您的完整網站 URL
```

### 第三步：驗證網站所有權

Google 會提供多種驗證方法：

#### 方法 1：HTML 檔案上傳
1. 下載 Google 提供的 HTML 驗證檔案
2. 上傳到您網站的根目錄
3. 確保可以通過 `https://您的網站.com/google-verification-file.html` 存取

#### 方法 2：HTML 標籤
1. 複製 Google 提供的 meta 標籤
2. 添加到網站首頁的 `<head>` 區段
```html
<meta name="google-site-verification" content="驗證碼" />
```

#### 方法 3：Google Analytics（如果已安裝）
1. 確保使用相同的 Google 帳戶
2. 網站已安裝 Google Analytics
3. 選擇「Google Analytics」驗證方法

#### 方法 4：Google Tag Manager（如果已安裝）
1. 確保使用相同的 Google 帳戶
2. 網站已安裝 Google Tag Manager
3. 選擇「Google Tag Manager」驗證方法

#### 方法 5：DNS 驗證（網域屬性）
1. 登入您的網域註冊商或 DNS 提供商
2. 添加 Google 提供的 TXT 記錄
```
記錄類型：TXT
主機：@
值：google-site-verification=驗證字串
```

### 第四步：完成驗證
1. 完成上述任一驗證方法
2. 回到 Search Console 點擊「驗證」
3. 驗證成功後，網站就會出現在您的屬性列表中

---

## 🎭 方案二：使用演示模式（暫時方案）

如果您暫時沒有網站或無法驗證，可以先使用演示模式體驗功能：

```bash
# 啟動演示版本（使用模擬數據）
python3 local_preview/app_simple.py

# 訪問 http://localhost:5001
# 體驗完整的 AIO 分析流程
```

演示模式特色：
- ✅ 使用真實的 Serper API
- ✅ 模擬 GSC 和 Google Ads 數據
- ✅ 完整的分析流程展示
- ✅ 真實的報告生成

---

## 🌟 方案三：使用測試網站

如果您想測試真實的 GSC API，可以使用以下方式：

### 選項 A：使用現有的網站
如果您有其他網站（個人網站、部落格等），可以：
1. 將該網站添加到 Search Console
2. 完成驗證
3. 使用該網站進行 API 測試

### 選項 B：創建免費測試網站
您可以快速創建一個免費網站進行測試：

**GitHub Pages（免費）**
1. 創建 GitHub 帳戶
2. 創建新的 repository
3. 啟用 GitHub Pages
4. 您會得到 `https://username.github.io/repository-name` 的網站
5. 將此網站添加到 Search Console

**Netlify（免費）**
1. 前往 netlify.com
2. 部署一個簡單的 HTML 頁面
3. 獲得免費的 .netlify.app 網域
4. 將此網站添加到 Search Console

**Vercel（免費）**
1. 前往 vercel.com
2. 部署一個簡單的靜態網站
3. 獲得免費的 .vercel.app 網域

---

## 📝 最小化測試網站範例

如果您想創建最簡單的測試網站，這裡是一個 HTML 範例：

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIO 分析器測試網站</title>
    <!-- Google Search Console 驗證標籤會放在這裡 -->
</head>
<body>
    <h1>AIO 分析器測試網站</h1>
    <p>這是用於測試 Google Search Console API 的網站。</p>
    
    <h2>測試內容</h2>
    <p>什麼是人工智慧？</p>
    <p>如何學習機器學習？</p>
    <p>什麼是 SEO 優化？</p>
    
    <footer>
        <p>&copy; 2024 AIO 分析器測試</p>
    </footer>
</body>
</html>
```

---

## 🚀 建議的操作順序

### 如果您有 SiEtrendforce 網站：
1. ✅ 添加網站到 Search Console
2. ✅ 完成所有權驗證
3. ✅ 設定服務帳戶權限
4. ✅ 測試 GSC API 連接

### 如果您暫時沒有網站：
1. ✅ 先使用演示模式體驗功能
2. ✅ 設定免費測試網站（可選）
3. ✅ 等待 SiEtrendforce 網站準備好後再設定

### 立即可用的方案：
```bash
# 立即體驗演示模式
export SERP_API_KEY="71951a3f6dd85b7d264d81b9ad88c3eccb429355"
python3 local_preview/app_simple.py
```

---

## ❓ 常見問題

**Q: 一定要有網站才能使用 AIO 分析器嗎？**
A: 不是！您可以使用演示模式體驗所有功能，或設定免費測試網站。

**Q: 驗證網站需要多長時間？**
A: HTML 檔案和標籤驗證通常是即時的，DNS 驗證可能需要幾小時。

**Q: 可以分析競爭對手的網站嗎？**
A: 不行，您只能分析自己擁有的網站。但可以使用其他工具（如 Serper API）分析公開的搜尋結果。

**Q: 如果我只想測試 AIO 檢測功能？**
A: 完美！Serper API 已經可以檢測 AI Overview，這是核心功能。

---

## 💡 推薦方案

基於您目前的情況，我建議：

1. **立即開始**：使用演示模式體驗功能
2. **並行準備**：如果有 SiEtrendforce 網站，同時進行 Search Console 設定
3. **逐步升級**：從演示模式 → 部分真實數據 → 完整真實數據

這樣您可以立即開始使用，同時逐步完善 API 設定！
