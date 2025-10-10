# pip install pandas numpy matplotlib seaborn

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# === CONFIG ===
CSV_PATH = os.getcwd() + "\\" + input("File name: ")

# === LOAD DATA ===
df = pd.read_csv(CSV_PATH)

# === DROP unnecessary columns ===
df = df.drop(columns=[col for col in df.columns if "Onay" in col], errors="ignore")

# === CONVERSIONS ===

# Gender: ERKEK=0, KIZ=1
df["Cinsiyet"] = df["Cinsiyet"].map({"ERKEK": 0, "KIZ": 1})

# School type: DEVLET=0, ÖZEL=1
df["Okul Türü"] = df["Okul Türü"].map({"DEVLET": 0, "ÖZEL": 1})

# Convert Hazırlık -> 8.5
df["Sınıf Seviyesi"] = df["Sınıf Seviyesi"].replace("Hazırlık", 8.5).astype(float)
df["Sınıf Seviyesi"] = pd.to_numeric(df["Sınıf Seviyesi"], errors="coerce")

# Convert numeric columns safely
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

# Most used platforms
platforms = ["Instagram", "TikTok", "YouTube", "Snapchat", "Facebook",
             "X (Twitter)", "Reddit", "Discord", "Pinterest", "LinkedIn", "Twitch"]

for p in platforms:
    df[p] = df["Sık Kullandığınız Platformlar"].apply(lambda x: 1 if p in str(x) else 0)

# Usage purpose
purposes = ["Sosyal Medya", "Oyun", "Eğitim", "Video / Film İzleme", "Spor"]

for p in purposes:
    df[p] = df["Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?"].apply(
        lambda x: 1 if p in str(x) else 0
    )

df = df.drop(columns=[
    "Sık Kullandığınız Platformlar",
    "Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?"
], errors="ignore")

# === CORRELATION ANALYSIS ===
plt.figure(figsize=(14,10))
corr = df.corr(numeric_only=True)
sns.heatmap(corr, cmap="coolwarm", annot=False)
plt.title("Değişkenler Arasındaki Korelasyon Haritası", fontsize=14)
plt.tight_layout()
plt.show(block=False)
plt.pause(0.001)

# === TOP CORRELATIONS ===
print("\nEn Güçlü Korelasyonlar:")
corr_pairs = corr.unstack().sort_values(ascending=False)
corr_pairs = corr_pairs[corr_pairs != 1.0]  # remove self correlations
print(corr_pairs.dropna().head(15))

# === SAMPLE RELATIONSHIPS ===
plt.figure(figsize=(8,6))
sns.scatterplot(data=df, x="Uyku Öncesi Telefon Kullanımı", y="Uyku Kalitesi")
plt.title("Uyku Öncesi Telefon Kullanımı (dk) vs Uyku Kalitesi")
plt.show(block=False)
plt.pause(0.001)

plt.figure(figsize=(8,6))
sns.scatterplot(data=df, x="Günlük Ekran Kullanım Süresi", y="Uyku Kalitesi")
plt.title("Ekran Süresi vs Uyku Kalitesi")
plt.show(block=False)
plt.pause(0.001)

plt.figure(figsize=(8,6))
sns.scatterplot(data=df, x="Haftalık Ders Çalışma Süresi", y="Son Dönem Not Ortalaması")
plt.title("Haftalık Ders Süresi vs Not Ortalaması")
plt.show(block=False)
plt.pause(0.001)

# === SUMMARY ===
print("\n--- Özet ---")
print("Toplam Katılımcı:", len(df))
print("Eksik Veriler:")
print(df.isna().sum())

input("Hepsini kapatmak için ENTER'a basın...")
plt.close('all')
