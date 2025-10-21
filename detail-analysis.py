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
UPLOAD = int(os.getenv("UPLOAD", 0))
SAVE = int(os.getenv("SAVE", 1))
DB_ACCESS = os.getenv("DB_ACCESS")

if not DB_ACCESS:
    print("⚠️ Warning: No DB_ACCESS found. Cloud upload will be skipped.")

pd.set_option('display.float_format', lambda x: f'{x:.2f}')
pd.set_option('future.no_silent_downcasting', True)
sns.set_theme(style="darkgrid")

# === CONFIG ===
CSV_PATH = "Büyük_Veri_Deneyi.csv"

# === LOAD ===
print("📊 Loading dataset...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"✅ Loaded {len(df)} entries and {len(df.columns)} columns.\n")

# === CLEANING ===
print("🧹 Cleaning data...")

# Drop unnecessary columns
df = df.drop(columns=[c for c in df.columns if "Onay" in c], errors="ignore")

# Mappings
df["Cinsiyet"] = df["Cinsiyet"].map({"ERKEK": 0, "KIZ": 1})
df["Okul Türü"] = df["Okul Türü"].map({"DEVLET": 0, "ÖZEL": 1})
df["Sınıf Seviyesi"] = df["Sınıf Seviyesi"].replace("Hazırlık", 8.5).astype(float)

# Numeric columns
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

# Expand multiple-choice questions
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

# Normalize numeric data
scaler = StandardScaler()
num_df = df.select_dtypes(include=[np.number])
df[num_df.columns] = scaler.fit_transform(num_df)

# Sanitize text
df = df.map(lambda x: str(x).replace("\n", " ") if isinstance(x, str) else x)

print("✅ Data cleaned and normalized.\n")

# === STATS ===
print("📈 Basic statistics:\n")
print(df.describe(include="all").transpose())
print("\nMissing values:\n", df.isna().sum())

# === CORRELATION ===
print("\n🔗 Computing correlations...")
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

# === ADVANCED SIGNIFICANCE TEST ===
def best_corr(x, y):
    """Adaptive correlation: Pearson if normal, Spearman otherwise"""
    if len(x) < 10 or len(y) < 10:
        return None, None
    try:
        if shapiro(x)[1] < 0.05 or shapiro(y)[1] < 0.05:
            return spearmanr(x, y)
        return pearsonr(x, y)
    except Exception:
        return None, None

print("\n📊 Statistically significant correlations (p < 0.05):")
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

# === CLOUD UPLOAD ===
if UPLOAD and DB_ACCESS:
    print("\n☁️ Uploading cleaned dataset to SQLiteCloud...")
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

# === SAVE LOCAL ===
if SAVE:
    try:
        df.to_csv("cleaned_data.csv", index=False)
        corr_pairs.to_csv("correlations.csv")
        print("\n💾 Saved cleaned data and correlation results to local files.")
    except Exception as e:
        print("⚠️ Saving failed:", e)

# === SUMMARY ===
print("\n--- SUMMARY ---")
print(f"Entries: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("Mean Sleep Quality:", df["Uyku Kalitesi"].mean().round(2) if "Uyku Kalitesi" in df else "N/A")
print("Mean Screen Time:", df["Günlük Ekran Kullanım Süresi"].mean().round(2) if "Günlük Ekran Kullanım Süresi" in df else "N/A")
print("Mean Academic Satisfaction:", df["Akademik Başarı Memnuniyeti"].mean().round(2) if "Akademik Başarı Memnuniyeti" in df else "N/A")

input("\nPress Enter to exit...")
