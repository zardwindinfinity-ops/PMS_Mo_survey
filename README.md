# 澳門公務員工作動機研究 — 問卷系統

績效指標體制與公共服務動機研究（情境實驗）

---

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `index.html` | 電子問卷主體，部署至 GitHub Pages |
| `apps-script.gs` | Google Apps Script，貼至 Google Sheets 接收問卷數據 |
| `analysis.py` | Python 統計分析腳本，直接從 Google Sheets 讀取數據 |

---

## 部署問卷（index.html）

### Step 1：建立 Google Sheets 試算表

1. 前往 [Google Sheets](https://sheets.google.com) 建立新試算表
2. 在第一行填入以下欄位標題（順序不能錯）：

```
timestamp | ref | scenario | A1 | A2 | A3 | B0 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 | Q11 | Q12 | Q13
```

### Step 2：部署 Google Apps Script

1. Google Sheets → **擴充功能** → **Apps Script**
2. 刪除預設代碼，貼上 `apps-script.gs` 的全部內容
3. **部署** → **新增部署作業** → 類型選「網頁應用程式」
4. 執行身分：**我**｜存取權限：**所有人**
5. 點擊部署，複製生成的**執行網址**

### Step 3：填入 Apps Script 網址

打開 `index.html`，找到以下這行並替換：

```javascript
const SHEETS_URL = 'YOUR_GOOGLE_APPS_SCRIPT_URL_HERE';
```

### Step 4：部署至 GitHub Pages

1. 建立新 Repository（例如 `macau-survey`）
2. 上傳 `index.html`（及本 README）至根目錄
3. **Settings** → **Pages** → Source 選 `main` / `root`
4. 約 1–2 分鐘後，問卷網址為：

```
https://[你的GitHub帳號].github.io/macau-survey/
```

---

## 情境分配

受試者使用同一條連結，系統自動隨機分配情境 A 或 B（50/50）。

研究人員預覽特定情境可在網址後加參數：

```
?scenario=A    # 強制顯示情境 A（支持型）
?scenario=B    # 強制顯示情境 B（控制型）
```

---

## 執行統計分析（analysis.py）

### 前置安裝（只需做一次）

```bash
pip install pandas scipy statsmodels openpyxl
```

### 設定 Google Sheets 連結

打開 `analysis.py`，在設定區填入試算表分享連結：

```python
SHEET_URL = "https://docs.google.com/spreadsheets/d/你的試算表ID/edit?usp=sharing"
```

> 試算表須設為「知道連結的人可以**檢視**」，腳本才能讀取數據。

### 執行方式

```bash
# 正式分析：從 Google Sheets 讀取真實問卷數據
python analysis.py

# 測試流程：使用模擬數據（N=200），無需網路連線
python analysis.py --demo

# 離線分析：使用已下載的本地 Excel 或 CSV 檔案
python analysis.py --file data.xlsx
python analysis.py --file data.csv

# 查看所有參數說明
python analysis.py --help
```

### 輸出結果

執行完成後，統計結果儲存至 `output/` 資料夾：

```
output/analysis_results_YYYYMMDD_HHMM.xlsx
```

Excel 內含以下分頁：

| 分頁 | 內容 |
|------|------|
| 原始數據 | 清理後的有效問卷（已通過操縱檢查） |
| 描述性統計 | 各構念 A/B 組均值、標準差 |
| 信度分析 | Cronbach's α |
| t檢定 | 獨立樣本 t 檢定，含 Cohen's d 效果量 |
| 本地化題項 | Q9、Q10 澳門本地化題項單獨分析 |
| 相關矩陣 | 皮爾遜相關係數 |
| 迴歸分析 | OLS 多元線性迴歸（依變數：離職傾向） |
| 統計摘要 | R²、F 值、樣本數、分析日期 |

---

## 問卷題目結構

| 題號 | 構念 | 量表 |
|------|------|------|
| A1–A3 | 基本資料 | 名義量表 |
| B0 | 操縱檢查 | 名義量表 |
| Q1–Q3 | 決策自主性 | Likert 1–5 |
| Q4–Q6 | 公共服務動機（PSM） | Likert 1–5 |
| Q7–Q10 | 離職傾向光譜 | Likert 1–5 |
| Q11–Q13 | 心理壓力與倦怠 | Likert 1–5 |

### 反向計分題（分析腳本自動處理）

Q4、Q5、Q6、Q13（新分數 = 6 − 原始分數）

### 操縱檢查篩選規則

| 組別 | 有效條件 |
|------|------|
| 情境 A（支持型） | B0 = 1 |
| 情境 B（控制型） | B0 = 2 |

---

## 數據欄位說明

| 欄位 | 說明 |
|------|------|
| timestamp | 提交時間（ISO 格式） |
| ref | 隨機參考編號 |
| scenario | A（支持型）或 B（控制型） |
| A1 | 職程類別（1=高技, 2=技術員, 3=技術輔導, 4=行政技術助理, 5=其他） |
| A2 | 年資（1=3年以下, 2=3–10年, 3=10–20年, 4=20年以上） |
| A3 | 崗位性質（1=前線, 2=後勤, 3=兩者兼有） |
| B0 | 操縱檢查（1=資源支援, 2=績效評核, 3=不確定） |
| Q1–Q13 | 各構念題項（Likert 1–5） |
