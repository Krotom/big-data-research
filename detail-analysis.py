# pip install pandas numpy matplotlib seaborn scipy sqlitecloud python-dotenv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from dotenv import load_dotenv
import sqlitecloud
import os

# --- ENVIRONMENT SETUP ---
load_dotenv()
UPLOAD = int(os.getenv("UPLOAD"))
SAVE = int(os.getenv("SAVE"))
DB_ACCESS = os.getenv("DB_ACCESS")

if not DB_ACCESS:
    raise ValueError("❌ Missing DB_ACCESS in .env file!")

pd.set_option('display.float_format', lambda x: f'{x:.2f}')
pd.set_option('future.no_silent_downcasting', True)
sns.set_theme(style="darkgrid")

# --- CONFIG ---
CSV_PATH = "Büyük_Veri_Deneyi.csv"

# --- LOAD ---
print("📊 Loading dataset...")
df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"✅ Loaded {len(df)} entries and {len(df.columns)} columns.\n")

# --- CLEAN ---
print("🧹 Cleaning data...")

# Drop "Onay" columns
df = df.drop(columns=[col for col in df.columns if "Onay" in col], errors="ignore")

# Replace and convert known mappings
if "Cinsiyet" in df.columns:
    df["Cinsiyet"] = df["Cinsiyet"].map({"ERKEK": 0, "KIZ": 1})
if "Okul Türü" in df.columns:
    df["Okul Türü"] = df["Okul Türü"].map({"DEVLET": 0, "ÖZEL": 1})
if "Sınıf Seviyesi" in df.columns:
    df["Sınıf Seviyesi"] = df["Sınıf Seviyesi"].replace("Hazırlık", 8.5).astype(float)

# Numeric conversions
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

# Expand multiple-choice columns
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

print("✅ Data cleaned successfully.\n")

# --- STATISTICS ---
print("📈 Basic statistics:\n")
print(df.describe(include="all").transpose())
print("\nMissing values:\n", df.isna().sum())

# --- CORRELATION MATRIX ---
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

# --- SIGNIFICANCE TESTS ---
print("\n📊 Statistically significant correlations (p < 0.05):")
for (a, b) in corr_pairs.head(30).index:
    x, y = df[a].dropna(), df[b].dropna()
    if len(x) > 5 and len(y) > 5:
        _, p = pearsonr(x, y)
        if p < 0.05:
            print(f"{a} ↔ {b}: r={corr.loc[a,b]:.2f}, p={p:.4f}")

if UPLOAD:
    # --- UPLOAD CLEANED DATA ---
    print("\n☁️ Uploading cleaned dataset to SQLiteCloud...")

    try:
        conn = sqlitecloud.connect(DB_ACCESS)
        cur = conn.cursor()

        # Drop the old table if exists
        cur.execute("DROP TABLE IF EXISTS bigdata_cleaned")

        # Create table with the same schema as the DataFrame
        cols = ", ".join([f'"{c}" TEXT' for c in df.columns])
        cur.execute(f"CREATE TABLE bigdata_cleaned ({cols});")

        # Insert all rows efficiently
        for _, row in df.iterrows():
            placeholders = ", ".join(["?" for _ in row])
            sql = f"INSERT INTO bigdata_cleaned VALUES ({placeholders});"
            cur.execute(sql, tuple(str(x) if pd.notna(x) else None for x in row))

        conn.commit()
        conn.close()
        print("✅ Uploaded successfully to SQLiteCloud.")

    except Exception as e:
        print("⚠️ Upload failed:", e)

if SAVE:
    print("\n🔗 Saving cleaned data and correlations...")
    try:
        df.to_csv("cleaned_data.csv", index=False)
        corr_pairs.to_csv("correlations.csv")
        print("✅ Saved successfully to local disk.")
    except Exception as e:
        print("⚠️ Saving failed:", e)

# --- SUMMARY ---
print("\n--- SUMMARY ---")
print(f"Entries: {len(df)}")
print(f"Columns: {len(df.columns)}")
print("Mean Sleep Quality:", df["Uyku Kalitesi"].mean().round(2))
print("Mean Screen Time:", df["Günlük Ekran Kullanım Süresi"].mean().round(2))
print("Mean Academic Satisfaction:", df["Akademik Başarı Memnuniyeti"].mean().round(2))

input("\nPress Enter to exit...")
