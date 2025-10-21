# pip install pandas numpy matplotlib seaborn python-dotenv

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# === CONFIG ===
load_dotenv()
CSV_PATH = os.path.join(os.getcwd(), input("File name: "))

# === LOAD DATA ===
df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded {len(df)} entries, {len(df.columns)} columns")

# === DROP unnecessary columns ===
df = df.drop(columns=[col for col in df.columns if "Onay" in col], errors="ignore")

# === CONVERSIONS ===
df["Cinsiyet"] = df["Cinsiyet"].map({"ERKEK": 0, "KIZ": 1})
df["Okul Türü"] = df["Okul Türü"].map({"DEVLET": 0, "ÖZEL": 1})
df["Sınıf Seviyesi"] = df["Sınıf Seviyesi"].replace("Hazırlık", 8.5).infer_objects(copy=False)
df["Sınıf Seviyesi"] = pd.to_numeric(df["Sınıf Seviyesi"], errors="coerce")

# Numeric columns
numeric_cols = [
    "Yaş", "Ortalama Uyku Süresi", "Uykuya Dalmada Zorluk Düzeyi",
    "Sabahları Alarm Erteleme Düzeyi", "Akademik Başarı Memnuniyeti",
    "Uyku Kalitesi", "Sabah Yorgun Uyanma Düzeyi", "Günlük Ekran Kullanım Süresi",
    "Son Dönem Not Ortalaması", "LGS Puanı", "Haftalık Ders Çalışma Süresi",
    "Derslerde Dikkat Dağınıklığı Düzeyi", "Günlük Kafein Tüketimi",
    "Haftalık Spor Yapma Sıklığı", "Genel Stres Düzeyi",
    "Uyku Öncesi Telefon Kullanımı"
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# === MULTIPLE CHOICE MAPPINGS ===
platforms = [
    "Instagram", "TikTok", "YouTube", "Snapchat", "Facebook",
    "X (Twitter)", "Reddit", "Discord", "Pinterest", "LinkedIn", "Twitch"
]
for p in platforms:
    df[p] = df["Sık Kullandığınız Platformlar"].astype(str).apply(lambda x: 1 if p in x else 0)

purposes = ["Sosyal Medya", "Oyun", "Eğitim", "Video / Film İzleme", "Spor"]
for p in purposes:
    df[p] = df["Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?"].astype(str).apply(
        lambda x: 1 if p in x else 0
    )

df = df.drop(columns=[
    "Sık Kullandığınız Platformlar",
    "Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?"
], errors="ignore")

# === DATA CLEANING ===
# Remove unrealistic outliers (3 std rule)
for col in numeric_cols:
    if col in df.columns:
        mean, std = df[col].mean(), df[col].std()
        df = df[(df[col] > mean - 3*std) & (df[col] < mean + 3*std)]

# Fill missing numeric values with median
df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

# === CORRELATION ANALYSIS ===
plt.figure(figsize=(16, 12))
corr = df.corr(numeric_only=True)
sns.heatmap(corr, cmap="coolwarm", annot=False)
plt.title("Değişkenler Arasındaki Korelasyon Haritası", fontsize=16)
plt.tight_layout()
plt.show(block=False)

# === TOP CORRELATIONS ===
print("\n📊 En Güçlü Korelasyonlar:")
mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
corr_pairs = corr.where(mask).unstack().dropna().sort_values(ascending=False)
print(corr_pairs.head(20))

# === SPEARMAN (for ranked data) ===
spearman_corr = df.corr(method="spearman", numeric_only=True)
print("\n📈 Spearman Korelasyon (Sıralı Değişkenler için):")
print(spearman_corr.unstack().sort_values(ascending=False).drop_duplicates().head(15))

# === VISUAL RELATIONSHIPS ===
plots = [
    ("Uyku Öncesi Telefon Kullanımı", "Uyku Kalitesi"),
    ("Günlük Ekran Kullanım Süresi", "Uyku Kalitesi"),
    ("Haftalık Ders Çalışma Süresi", "Son Dönem Not Ortalaması"),
    ("Genel Stres Düzeyi", "Uyku Kalitesi"),
]
for x, y in plots:
    if x in df.columns and y in df.columns:
        plt.figure(figsize=(8,6))
        sns.regplot(data=df, x=x, y=y, scatter_kws={'alpha':0.6})
        plt.title(f"{x} vs {y}")
        plt.show(block=False)
        plt.pause(0.001)

# === SUMMARY ===
print("\n--- 📋 Özet ---")
print(f"Toplam Katılımcı: {len(df)}")
print("\nEksik Veriler:")
print(df.isna().sum()[df.isna().sum() > 0])

input("\nENTER'a basarak tüm grafikleri kapatın...")
plt.close('all')
