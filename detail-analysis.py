# pip install pandas numpy matplotlib seaborn scipy sqlitecloud python-dotenv scikit-learn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr, shapiro
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv
import sqlitecloud
import os

# === ENVIRONMENT SETUP ===
load_dotenv()
CSV_PATH = os.getenv("FILE_NAME", "Büyük_Veri_Deneyi.csv")
UPLOAD = int(os.getenv("UPLOAD", 0))
SAVE = int(os.getenv("SAVE", 1))
DB_ACCESS = os.getenv("DB_ACCESS")

if not DB_ACCESS:
    print("⚠️ Warning: No DB_ACCESS found. Cloud upload will be skipped.")

pd.set_option('display.float_format', lambda x: f'{x:.2f}')
pd.set_option('future.no_silent_downcasting', True)
sns.set_theme(style="darkgrid")

# === LOAD ===
print("📊 Loading dataset...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"✅ Loaded {len(df)} entries and {len(df.columns)} columns.\n")

# === CLEANING ===
print("🧹 Cleaning data...")

df = df.drop(columns=[c for c in df.columns if "Onay" in c], errors="ignore")

df["Cinsiyet"] = df["Cinsiyet"].map({"ERKEK": 0, "KIZ": 1})
df["Okul Türü"] = df["Okul Türü"].map({"DEVLET": 0, "ÖZEL": 1})
df["Sınıf Seviyesi"] = df["Sınıf Seviyesi"].replace("Hazırlık", 8.5).astype(float)

num_cols = [
    "Yaş","Ortalama Uyku Süresi","Uykuya Dalmada Zorluk Düzeyi",
    "Sabahları Alarm Erteleme Düzeyi","Akademik Başarı Memnuniyeti",
    "Uyku Kalitesi","Sabah Yorgun Uyanma Düzeyi","Günlük Ekran Kullanım Süresi",
    "Son Dönem Not Ortalaması","LGS Puanı","Haftalık Ders Çalışma Süresi",
    "Derslerde Dikkat Dağınıklığı Düzeyi","Günlük Kafein Tüketimi",
    "Haftalık Spor Yapma Sıklığı","Genel Stres Düzeyi","Uyku Öncesi Telefon Kullanımı"
]
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

def expand_multichoice(df, col, options):
    for opt in options:
        df[opt] = df[col].apply(lambda x: 1 if opt in str(x) else 0)
    return df.drop(columns=[col], errors="ignore")

if "Sık Kullandığınız Platformlar" in df.columns:
    df = expand_multichoice(df, "Sık Kullandığınız Platformlar", [
        "Instagram","TikTok","YouTube","Snapchat","Facebook",
        "X (Twitter)","Reddit","Discord","Pinterest","LinkedIn","Twitch"
    ])

if "Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?" in df.columns:
    df = expand_multichoice(df, "Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?", [
        "Sosyal Medya","Oyun","Eğitim","Video / Film İzleme","Spor"
    ])

# Remove outliers (3-sigma)
for c in num_cols:
    if c in df.columns:
        df = df[np.abs(df[c] - df[c].mean()) <= (3 * df[c].std())]

# Normalize
scaler = StandardScaler()
num_df = df.select_dtypes(include=[np.number])
df[num_df.columns] = scaler.fit_transform(num_df)

df = df.map(lambda x: str(x).replace("\n", " ") if isinstance(x, str) else x)
print("✅ Data cleaned and normalized.\n")

# === CORRELATION ===
corr = df.corr(numeric_only=True)
mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
corr_pairs = corr.where(mask).unstack().dropna().sort_values(ascending=False)

plt.figure(figsize=(16,12))
sns.heatmap(corr, cmap="coolwarm", annot=False)
plt.title("Korelasyon Haritası")
plt.tight_layout()
plt.show(block=False)
plt.pause(0.001)

print("\nTop correlation pairs:")
print(corr_pairs.head(15))

# === SMART CORRELATION ===
def best_corr(x, y):
    if len(x) < 10 or len(y) < 10:
        return None, None
    try:
        if shapiro(x)[1] < 0.05 or shapiro(y)[1] < 0.05:
            return spearmanr(x, y)
        return pearsonr(x, y)
    except Exception:
        return None, None

print("\n📊 Significant correlations (p < 0.05):")
for (a, b) in corr_pairs.head(40).index:
    x, y = df[a].dropna(), df[b].dropna()
    r, p = best_corr(x, y)
    if r is not None and p < 0.05:
        print(f"{a} ↔ {b}: r={r:.2f}, p={p:.4f}")

# === AUTO INSIGHTS ===
print("\n🧠 Auto Insights:")
for (a, b), r in corr_pairs.head(10).items():
    direction = "increases" if r > 0 else "decreases"
    strength = "strongly" if abs(r) > 0.6 else "moderately" if abs(r) > 0.3 else "weakly"
    print(f"As {a} increases, {b} {strength} {direction} (r={r:.2f})")

# === INTERACTIVE CORRELATION LOOP ===
while True:
    print("\n🔍 Manual Correlation Checker")
    print("Type two column names to analyze, or press ENTER to exit.\n")
    print("Available columns:")
    print(", ".join(df.columns[:10]), "...")
    col1 = input("\nColumn 1: ").strip()
    if not col1:
        break
    col2 = input("Column 2: ").strip()
    if not col2:
        break
    if col1 not in df.columns or col2 not in df.columns:
        print("⚠️ Invalid column names, try again.")
        continue
    x, y = df[col1].dropna(), df[col2].dropna()
    r_p, p_p = pearsonr(x, y)
    r_s, p_s = spearmanr(x, y)
    print(f"\nPearson: r={r_p:.3f}, p={p_p:.5f}")
    print(f"Spearman: r={r_s:.3f}, p={p_s:.5f}")

    sns.lmplot(x=col1, y=col2, data=df, line_kws={'color': 'red'}, scatter_kws={'alpha':0.5})
    plt.title(f"{col1} vs {col2}\nPearson r={r_p:.2f}, Spearman r={r_s:.2f}")
    plt.show(block=False)
    plt.pause(0.001)

# === SAVE ===
if SAVE:
    df.to_csv("cleaned_data.csv", index=False)
    corr_pairs.to_csv("correlations.csv")
    print("\n💾 Saved cleaned data and correlations locally.")

# === UPLOAD ===
if UPLOAD and DB_ACCESS:
    try:
        conn = sqlitecloud.connect(DB_ACCESS)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS bigdata_cleaned")
        cols = ", ".join([f'"{c}" TEXT' for c in df.columns])
        cur.execute(f"CREATE TABLE bigdata_cleaned ({cols});")
        sql = f"INSERT INTO bigdata_cleaned VALUES ({', '.join(['?' for _ in df.columns])});"
        cur.executemany(sql, df.astype(str).fillna("").values.tolist())
        conn.commit()
        conn.close()
        print("✅ Uploaded successfully to SQLiteCloud.")
    except Exception as e:
        print("⚠️ Upload failed:", e)

# === SUMMARY ===
print("\n--- SUMMARY ---")
print(f"Entries: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("Mean Sleep Quality:", df["Uyku Kalitesi"].mean().round(2) if "Uyku Kalitesi" in df else "N/A")
print("Mean Screen Time:", df["Günlük Ekran Kullanım Süresi"].mean().round(2) if "Günlük Ekran Kullanım Süresi" in df else "N/A")
print("Mean Academic Satisfaction:", df["Akademik Başarı Memnuniyeti"].mean().round(2) if "Akademik Başarı Memnuniyeti" in df else "N/A")

input("\nPress Enter to exit...")
