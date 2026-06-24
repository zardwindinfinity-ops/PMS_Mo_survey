# PMS_Mo_survey
績效指標體制、動機擠出效應與公務員離職傾向光譜  ——澳門電子政務背景下的情境實驗研究
# 問卷部署說明

## 結構說明

```
survey/
├── index.html          ← 問卷主體（放到 GitHub Pages）
├── apps-script.gs      ← Google Apps Script（貼到 Google Sheets）
└── README.md           ← 本說明文件
```

---

## Step 1：建立 Google Sheets 試算表

1. 前往 [Google Sheets](https://sheets.google.com) 建立新試算表
2. 將試算表命名為「澳門公務員問卷數據」
3. 在 **第一行（A1 開始）** 填入以下欄位標題（順序不能錯）：

```
timestamp | ref | scenario | A1 | A2 | A3 | B0 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13
```

---

## Step 2：部署 Google Apps Script

1. 在 Google Sheets → 選單 **「擴充功能」** → **「Apps Script」**
2. 刪除預設的 `function myFunction() {}` 代碼
3. 將 `apps-script.gs` 檔案的全部內容貼上
4. 點擊 **「部署」** → **「新增部署作業」**
5. 選擇類型：**「網頁應用程式」**
6. 設定：
   - 執行身分：**「我」**
   - 存取權限：**「所有人」**（重要！否則問卷無法提交）
7. 點擊 **「部署」**，複製生成的 **執行網址（URL）**

---

## Step 3：填入 Sheets URL

打開 `index.html`，找到這一行：

```javascript
const SHEETS_URL = 'YOUR_GOOGLE_APPS_SCRIPT_URL_HERE';
```

將引號內的文字替換為剛才複製的執行網址，例如：

```javascript
const SHEETS_URL = 'https://script.google.com/macros/s/AKfycby.../exec';
```

---

## Step 4：部署到 GitHub Pages

1. 在 GitHub 建立新 Repository（例如：`macau-survey`）
2. 將 `index.html` 上傳到 Repository 根目錄
3. 進入 Repository → **Settings** → **Pages**
4. Source 選擇：**Deploy from a branch** → **main** → **/ (root)**
5. 儲存後約 1–2 分鐘，即可透過以下網址訪問問卷：

```
https://[你的GitHub帳號].github.io/macau-survey/
```

---

## 情境分配說明

- **正常填答**：系統自動隨機分配情境 A 或 B（50/50 機率）
- **研究人員預覽特定情境**：在網址後加上參數：
  - `?scenario=A` → 強制顯示情境 A（支持型）
  - `?scenario=B` → 強制顯示情境 B（控制型）

---

## 數據欄位說明

| 欄位 | 說明 |
|------|------|
| timestamp | 提交時間（ISO 格式） |
| ref | 隨機參考編號（用於確認提交） |
| scenario | A（支持型）或 B（控制型） |
| A1 | 職程類別（1=高技, 2=技術員, 3=技術輔導, 4=行政技術助理, 5=其他） |
| A2 | 年資（1=3年以下, 2=3–10年, 3=10–20年, 4=20年以上） |
| A3 | 崗位性質（1=前線, 2=後勤, 3=兩者兼有） |
| B0 | 操縱檢查（1=資源支援, 2=績效評核, 3=不確定） |
| Q1–Q3 | 決策自主性（1–5 Likert） |
| Q4–Q6 | 工作動機 PSM（1–5，Q4–Q6 為反向計分題） |
| Q7–Q10 | 離職傾向光譜（Q9、Q10 為澳門本地化題） |
| Q11–Q13 | 心理壓力與倦怠（Q13 為反向計分題） |

---

## 操縱檢查篩選規則

施測完成後，在 Google Sheets 中按以下規則篩選有效問卷：

- **情境 A 組**（scenario = A）：B0 = 1 → 有效；B0 ≠ 1 → 剔除
- **情境 B 組**（scenario = B）：B0 = 2 → 有效；B0 ≠ 2 → 剔除

---

## 反向計分規則（分析時使用）

以下題目需在分析前反向計分（新分數 = 6 - 原始分數）：

| 題號 | 構念 |
|------|------|
| Q4 | PSM — 方向目標一致感 |
| Q5 | PSM — 專業成就感 |
| Q6 | PSM — 持續投入意願 |
| Q13 | 倦怠感 — 耐心維持（反向） |

---

## 構念對應關係

| 構念 | 題號 | 論文量表對應 |
|------|------|------------|
| 決策自主性 | Q1–Q3 | 本研究自編 |
| 工作動機（PSM） | Q4–Q6 | Kim et al. (2013) 改編 |
| 離職傾向光譜 | Q7–Q10 | Mobley (1977) + 本研究澳門化題項 |
| 心理壓力與倦怠 | Q11–Q13 | 本研究自編 |
