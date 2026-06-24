// ══════════════════════════════════════════════════════════════
//  澳門公務員問卷 — Google Apps Script 接收腳本
//  貼至：Google Sheets → 擴充功能 → Apps Script
// ══════════════════════════════════════════════════════════════

const SHEET_NAME = 'Sheet1'; // 若你的分頁名稱不同，請修改此處

// 欄位順序（需與 Google Sheets 第一行標題一致）
const COLUMNS = [
  'timestamp', 'ref', 'scenario',
  'A1', 'A2', 'A3',
  'B0',
  'Q1', 'Q2', 'Q3',
  'Q4', 'Q5', 'Q6',
  'Q7', 'Q8', 'Q9', 'Q10',
  'Q11', 'Q12', 'Q13'
];

// ── 接收 POST 請求 ──
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);

    // 按欄位順序組成一行
    const row = COLUMNS.map(col => data[col] !== undefined ? data[col] : '');
    sheet.appendRow(row);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok', ref: data.ref }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// ── 測試用（可在 Apps Script 編輯器手動執行）──
function testSetup() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) {
    Logger.log('❌ 找不到分頁：' + SHEET_NAME);
    return;
  }
  Logger.log('✅ 連接成功，目前共有 ' + (sheet.getLastRow() - 1) + ' 筆有效問卷數據');
}
