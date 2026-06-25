"""
澳門公務員工作動機研究 — 數據分析腳本
=========================================
直接從 Google Sheets 讀取問卷數據並執行完整統計分析。

使用方法：
    python analysis.py                        # 從 Google Sheets 讀取真實數據
    python analysis.py --demo                 # 使用模擬數據（N=200）測試流程
    python analysis.py --file data.xlsx       # 讀取本地 Excel 檔案
    python analysis.py --file data.csv        # 讀取本地 CSV 檔案

前置設定（只需做一次）：
    pip install pandas scipy statsmodels openpyxl

Google Sheets 連接設定：
    將下方 SHEET_URL 替換為你的試算表分享連結
    （試算表 → 分享 → 知道連結的人可以檢視 → 複製連結）
"""

import warnings
warnings.filterwarnings('ignore')

import argparse
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from datetime import datetime
import os

# ══════════════════════════════════════════
#  設定區（修改這裡）
# ══════════════════════════════════════════

# 方法一：直接讀取 Google Sheets（試算表須設為「知道連結的人可以檢視」）
# 將試算表分享連結貼在此處，例如：
# https://docs.google.com/spreadsheets/d/1ABC.../edit?usp=sharing
SHEET_URL = "https://docs.google.com/spreadsheets/d/1qfAlefs8SYLEir5NoCQjq-D5kGmlXtAnPhSN1SH-7kA/edit?usp=sharing"

# 方法二：若已下載 Excel/CSV，填入本地檔案路徑（留空則使用 Google Sheets）
LOCAL_FILE = "data.xlsx"   # 例如 "data.xlsx" 或 "data.csv"


# 輸出資料夾
OUTPUT_DIR = "output"

# ══════════════════════════════════════════
#  構念定義
# ══════════════════════════════════════════

# 反向計分題（原始分數需轉換：新分 = 6 - 原分）
REVERSE_ITEMS = ['Q4', 'Q5', 'Q6', 'Q13']

# 各構念對應題號
CONSTRUCTS = {
    'decision_autonomy': ['Q1', 'Q2', 'Q3'],          # 決策自主性
    'psm':               ['Q4', 'Q5', 'Q6'],           # 公共服務動機
    'turnover':          ['Q7', 'Q8', 'Q9', 'Q10'],   # 離職傾向光譜
    'burnout':           ['Q11', 'Q12', 'Q13'],        # 心理壓力與倦怠
}

CONSTRUCT_LABELS = {
    'decision_autonomy': '決策自主性',
    'psm':               '公共服務動機（PSM）',
    'turnover':          '離職傾向光譜',
    'burnout':           '心理壓力與倦怠',
}

# ══════════════════════════════════════════
#  資料載入
# ══════════════════════════════════════════

def load_data(use_demo=False, local_file=""):
    """
    載入數據，優先順序如下：
      1. --demo        → 使用模擬數據（測試分析流程用）
      2. --file <路徑> → 讀取本地 Excel / CSV
      3. 預設          → 從 SHEET_URL 的 Google Sheets 即時下載

    本研究使用方式：不加任何參數，直接從 Google Sheets 讀取問卷回收數據。
    """

    # ── --demo：模擬數據 ──
    if use_demo:
        print("🧪 使用模擬數據（N=200）")
        return generate_demo_data()

    # ── --file：本地檔案 ──
    if local_file and os.path.exists(local_file):
        print(f"📂 從本地檔案載入：{local_file}")
        return pd.read_csv(local_file) if local_file.endswith(".csv") else pd.read_excel(local_file)

    # ── 預設：Google Sheets ──
    print("☁️  從 Google Sheets 載入數據…")
    # 分享連結格式為 /edit?usp=sharing，需替換為 /export?format=csv 才能讀取
    csv_url = SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    df = pd.read_csv(csv_url)
    print(f"   ✅ 成功載入 {len(df)} 筆記錄")
    return df


def generate_demo_data(n=200, seed=42):
    """
    生成模擬數據（與論文附錄二參數一致）

    修正說明：
    1. 使用多變量正態分佈（ρ=0.50）確保題目間有合理相關，Cronbach's α才能達標
    2. 反向計分題（Q4/Q5/Q6/Q13）在生成時使用反向均值（6-目標值），
       反向計分後才還原為目標方向，避免PSM方向錯誤
    3. 使用 scipy.stats.multivariate_normal 確保可重現性
    """
    from scipy.stats import multivariate_normal as mvn

    np.random.seed(seed)  # 使用 numpy seed 確保可重現

    # 各構念目標均值（計分後的期望值）
    params = {
        'A': {'decision_autonomy': 4.0, 'psm': 4.1, 'turnover': 2.1, 'burnout': 2.1},
        'B': {'decision_autonomy': 2.8, 'psm': 2.8, 'turnover': 3.7, 'burnout': 3.9},
    }

    rho = 0.50   # 題目間相關係數
    sd  = 0.65   # 標準差

    rows = []
    for i in range(n):
        g = 'A' if i < n // 2 else 'B'
        p = params[g]
        row = {
            'scenario': g,
            'timestamp': datetime.now().isoformat(),
            'ref': f'SIM{i:04d}',
            'A1': int(np.random.randint(1, 6)),
            'A2': int(np.random.randint(1, 5)),
            'A3': int(np.random.randint(1, 4)),
            'B0': 1 if g == 'A' else 2,
        }
        for name, mu_target in p.items():
            items = CONSTRUCTS[name]
            k = len(items)

            # 反向計分題在生成時用反向均值，確保計分後方向正確
            means = []
            for item in items:
                if item in REVERSE_ITEMS:
                    means.append(6 - mu_target)  # 生成反向均值
                else:
                    means.append(mu_target)

            # 建立相關矩陣（題目間相關 ρ）
            cov = [[sd**2 if ii == jj else rho * sd**2
                    for jj in range(k)] for ii in range(k)]

            # 多變量正態生成
            vals = mvn.rvs(mean=means, cov=cov)
            if k == 1:
                vals = [vals]
            vals = np.clip(np.round(vals), 1, 5).astype(int)

            for item, v in zip(items, vals):
                row[item] = int(v)

        rows.append(row)

    return pd.DataFrame(rows)


# ══════════════════════════════════════════
#  資料清理
# ══════════════════════════════════════════

def clean_data(df):
    """清理數據並套用反向計分"""
    print("\n📋 資料清理")
    print(f"   原始筆數：{len(df)}")

    # 操縱檢查篩選
    valid_mask = (
        ((df['scenario'] == 'A') & (df['B0'] == 1)) |
        ((df['scenario'] == 'B') & (df['B0'] == 2))
    )
    df = df[valid_mask].copy()
    print(f"   通過操縱檢查：{len(df)} 筆（通過率 {len(df)/len(df if len(df)>0 else [1])*100:.1f}%）")

    # 反向計分
    for item in REVERSE_ITEMS:
        if item in df.columns:
            df[item + '_r'] = 6 - df[item]
            df[item] = df[item + '_r']

    # 計算各構念合成分數
    for name, items in CONSTRUCTS.items():
        df[name + '_score'] = df[items].mean(axis=1)

    # 分組
    df_a = df[df['scenario'] == 'A']
    df_b = df[df['scenario'] == 'B']
    print(f"   情境 A（支持型）：{len(df_a)} 人")
    print(f"   情境 B（控制型）：{len(df_b)} 人")

    return df, df_a, df_b


# ══════════════════════════════════════════
#  統計分析
# ══════════════════════════════════════════

def cronbach_alpha(df_items):
    """計算 Cronbach's α"""
    k = df_items.shape[1]
    item_vars = df_items.var(axis=0, ddof=1).sum()
    total_var = df_items.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars / total_var)


def cohens_d(a, b):
    """計算 Cohen's d 效果量"""
    pooled_sd = np.sqrt((a.std(ddof=1)**2 + b.std(ddof=1)**2) / 2)
    return (a.mean() - b.mean()) / pooled_sd


def run_analysis(df, df_a, df_b):
    results = {}

    # ── 1. 描述性統計 ──
    print("\n" + "═"*60)
    print("1. 描述性統計")
    print("═"*60)
    desc_rows = []
    for name, label in CONSTRUCT_LABELS.items():
        col = name + '_score'
        for g, gdf in [('支持型（A）', df_a), ('控制型（B）', df_b)]:
            s = gdf[col]
            desc_rows.append({
                '構念': label, '組別': g,
                'N': len(s), 'M': round(s.mean(), 2), 'SD': round(s.std(), 2),
                'Min': round(s.min(), 2), 'Max': round(s.max(), 2)
            })
    desc_df = pd.DataFrame(desc_rows)
    print(desc_df.to_string(index=False))
    results['descriptives'] = desc_df

    # ── 2. 信度分析 ──
    print("\n" + "═"*60)
    print("2. Cronbach's α 信度分析")
    print("═"*60)
    alpha_rows = []
    for name, items in CONSTRUCTS.items():
        alpha = cronbach_alpha(df[items])
        status = "✅" if alpha >= 0.7 else "⚠️ 偏低"
        print(f"   {CONSTRUCT_LABELS[name]:20s}  α = {alpha:.3f}  {status}")
        alpha_rows.append({'構念': CONSTRUCT_LABELS[name], 'α': round(alpha, 3), '題數': len(items)})
    results['reliability'] = pd.DataFrame(alpha_rows)

    # ── 3. 獨立樣本 t 檢定（H1、H2）──
    print("\n" + "═"*60)
    print("3. 獨立樣本 t 檢定")
    print("═"*60)
    ttest_rows = []
    for name, label in CONSTRUCT_LABELS.items():
        col = name + '_score'
        a_vals = df_a[col].dropna()
        b_vals = df_b[col].dropna()
        t, p = stats.ttest_ind(a_vals, b_vals)
        d = cohens_d(a_vals, b_vals)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        print(f"   {label:22s}  t = {t:6.2f}  p = {p:.4f} {sig}  d = {abs(d):.2f}")
        ttest_rows.append({
            '構念': label, 't值': round(t, 2), 'p值': round(p, 4),
            '顯著性': sig, "Cohen's d": round(abs(d), 2),
            'A組均值': round(a_vals.mean(), 2), 'B組均值': round(b_vals.mean(), 2)
        })
    results['ttest'] = pd.DataFrame(ttest_rows)

    # ── 4. 澳門本地化題項（G4=Q10, G5=Q9, G6=Q9 對應）──
    print("\n" + "═"*60)
    print("4. 澳門本地化題項分析（離職傾向光譜）")
    print("═"*60)
    local_items = {'Q9（薪酬工具性投入）': 'Q9', 'Q10（熬退休傾向）': 'Q10'}
    local_rows = []
    for label, item in local_items.items():
        a_m = df_a[item].mean()
        b_m = df_b[item].mean()
        t, p = stats.ttest_ind(df_a[item], df_b[item])
        d = cohens_d(df_a[item], df_b[item])
        print(f"   {label:25s}  A={a_m:.2f}  B={b_m:.2f}  Δ={b_m-a_m:+.2f}  d={abs(d):.2f}")
        local_rows.append({'題目': label, 'A組': round(a_m, 2), 'B組': round(b_m, 2),
                           'Δ': round(b_m - a_m, 2), "Cohen's d": round(abs(d), 2)})
    results['localized'] = pd.DataFrame(local_rows)

    # ── 5. 皮爾遜相關矩陣 ──
    print("\n" + "═"*60)
    print("5. 皮爾遜相關矩陣")
    print("═"*60)
    score_cols = [n + '_score' for n in CONSTRUCT_LABELS.keys()]
    short_labels = ['自主性', 'PSM', '離職傾向', '倦怠感']
    corr_df = df[score_cols].copy()
    corr_df.columns = short_labels
    corr_matrix = corr_df.corr()
    print(corr_matrix.round(3).to_string())
    results['correlation'] = corr_matrix

    # ── 6. OLS 多元迴歸 ──
    print("\n" + "═"*60)
    print("6. OLS 多元線性迴歸（依變數：離職傾向）")
    print("═"*60)
    df_reg = df.copy()
    df_reg['group_dummy'] = (df_reg['scenario'] == 'B').astype(int)

    X = df_reg[['group_dummy', 'psm_score', 'decision_autonomy_score', 'burnout_score']]
    X = sm.add_constant(X)
    y = df_reg['turnover_score']

    model = sm.OLS(y, X).fit()
    print(model.summary().tables[1])
    print(f"\n   R² = {model.rsquared:.3f}   Adj.R² = {model.rsquared_adj:.3f}")
    results['regression'] = model

    return results


# ══════════════════════════════════════════
#  輸出 Excel 報告
# ══════════════════════════════════════════

def export_excel(df, results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fname = os.path.join(OUTPUT_DIR, f"analysis_results_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")

    with pd.ExcelWriter(fname, engine='openpyxl') as writer:
        # 原始數據
        df.to_excel(writer, sheet_name='原始數據', index=False)

        # 各分析結果
        results['descriptives'].to_excel(writer, sheet_name='描述性統計', index=False)
        results['reliability'].to_excel(writer, sheet_name='信度分析', index=False)
        results['ttest'].to_excel(writer, sheet_name='t檢定', index=False)
        results['localized'].to_excel(writer, sheet_name='本地化題項', index=False)
        results['correlation'].round(3).to_excel(writer, sheet_name='相關矩陣')

        # 迴歸摘要
        reg = results['regression']
        reg_summary = pd.DataFrame({
            '變數': reg.params.index,
            'β係數': reg.params.round(3).values,
            '標準誤': reg.bse.round(3).values,
            't值': reg.tvalues.round(3).values,
            'p值': reg.pvalues.round(4).values,
        })
        reg_summary.to_excel(writer, sheet_name='迴歸分析', index=False)

        # 附加統計摘要
        stat_notes = pd.DataFrame([
            ['R²', f"{reg.rsquared:.3f}"],
            ['Adj.R²', f"{reg.rsquared_adj:.3f}"],
            ['F統計量', f"{reg.fvalue:.2f}"],
            ['模型p值', f"{reg.f_pvalue:.4f}"],
            ['樣本數（有效）', str(len(df))],
            ['分析日期', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ], columns=['指標', '數值'])
        stat_notes.to_excel(writer, sheet_name='統計摘要', index=False)

    print(f"\n✅ Excel 報告已儲存：{fname}")
    return fname


# ══════════════════════════════════════════
#  主程式
# ══════════════════════════════════════════

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='澳門公務員工作動機研究 — 統計分析')
    parser.add_argument('--demo', action='store_true', help='使用模擬數據（N=200）')
    parser.add_argument('--file', type=str, default='', help='本地 Excel/CSV 檔案路徑')
    args = parser.parse_args()

    # 命令列參數覆蓋設定區的預設值
    USE_DEMO  = args.demo
    if args.file:
        LOCAL_FILE = args.file

    print("=" * 60)
    print("  澳門公務員工作動機研究 — 統計分析")
    print("=" * 60)

    df_raw = load_data(use_demo=USE_DEMO, local_file=LOCAL_FILE if args.file else '')
    df, df_a, df_b = clean_data(df_raw)
    results = run_analysis(df, df_a, df_b)
    export_excel(df, results)

    print("\n🎓 分析完成。")