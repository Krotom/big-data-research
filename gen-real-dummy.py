import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

n = 30
np.random.seed(42)

def random_time(mean_hour, stddev=0.5):
    """Generate realistic time strings centered around mean_hour (24h)"""
    hour = np.clip(np.random.normal(mean_hour, stddev), 0, 23)
    minute = random.choice([0, 15, 30, 45])
    return f"{int(hour):02d}:{minute:02d}"

def random_multi(options, probs, min_n=1, max_n=3):
    k = random.randint(min_n, max_n)
    return "\n".join(np.random.choice(options, k, replace=False, p=probs))

platforms = ["Instagram","TikTok","YouTube","Snapchat","Facebook",
             "X (Twitter)","Reddit","Discord","Pinterest","LinkedIn","Twitch"]
platform_probs = [0.25,0.15,0.3,0.05,0.02,0.05,0.03,0.08,0.02,0.02,0.03]

purposes = ["Sosyal Medya","Oyun","Eğitim","Video / Film İzleme","Spor"]
purpose_probs = [0.45,0.25,0.15,0.10,0.05]

rows = []

for _ in range(n):
    gender = np.random.choice(["ERKEK", "KIZ"], p=[0.55, 0.45])
    age = np.random.choice([14,15,16,17])
    grade = np.random.choice(["Hazırlık", "9", "10", "11", "12"], p=[0.1,0.3,0.25,0.2,0.15])
    school = np.random.choice(["DEVLET", "ÖZEL"], p=[0.7,0.3])

    # Sleep patterns
    sleep_avg = np.clip(np.random.normal(7.5, 0.8), 5, 10)
    weekday_sleep = random_time(23 if age>14 else 22)
    weekday_wake = random_time(7 if age>14 else 6.5)
    weekend_sleep = random_time(24)
    weekend_wake = random_time(9)
    sleep_diff = int(np.clip(np.random.normal(2,1),1,5))
    snooze = int(np.clip(np.random.normal(3,1),1,5))
    academic_sat = int(np.clip(np.random.normal(3.5,1),1,5))
    sleep_quality = int(np.clip(10 - (sleep_diff + np.random.normal(0,1)), 3,10))
    tired_morning = int(np.clip((6 - sleep_quality/2) + np.random.normal(0,0.5), 1,5))
    screen_time = np.clip(np.random.normal(4,1.5), 1,8)

    used_platforms = random_multi(platforms, platform_probs, 2, 5)
    usage_purpose = random_multi(purposes, purpose_probs, 1, 3)

    gpa = int(np.clip(np.random.normal(85 - (screen_time*2), 7), 55,100))
    lgs = int(np.clip(np.random.normal(400 - (screen_time*10), 50), 250,500))
    study_hours = int(np.clip(np.random.normal(12 - screen_time/2, 4), 1,25))
    attention = int(np.clip(np.random.normal(3.5 - (screen_time/4),1),1,5))
    caffeine = int(np.clip(np.random.normal(screen_time/3,1),0,5))
    sport_freq = int(np.clip(np.random.normal(3,2),0,7))
    stress = int(np.clip(np.random.normal(3 + (screen_time-3)/3,1),1,5))
    phone_before_sleep = int(np.clip(np.random.normal(45 + screen_time*5, 15), 5,120))

    rows.append({
        "Submission Date": "Eki 9, 2025",
        "Onay": "Kabul Edildi",
        "Cinsiyet": gender,
        "Yaş": age,
        "Sınıf Seviyesi": grade,
        "Okul Türü": school,
        "Ortalama Uyku Süresi": round(sleep_avg,1),
        "Hafta İçi Uyuma Saati": weekday_sleep,
        "Hafta İçi Uyanma Saati": weekday_wake,
        "Hafta Sonu Uyuma Saati": weekend_sleep,
        "Hafta Sonu Uyanma Saati": weekend_wake,
        "Uykuya Dalmada Zorluk Düzeyi": sleep_diff,
        "Sabahları Alarm Erteleme Düzeyi": snooze,
        "Akademik Başarı Memnuniyeti": academic_sat,
        "Uyku Kalitesi": sleep_quality,
        "Sabah Yorgun Uyanma Düzeyi": tired_morning,
        "Günlük Ekran Kullanım Süresi": round(screen_time,1),
        "Sık Kullandığınız Platformlar": used_platforms,
        "Telefon, PC gibi teknolojik cihazları genellikle hangi amaçla kullanıyorsunuz?": usage_purpose,
        "Son Dönem Not Ortalaması": gpa,
        "LGS Puanı": lgs,
        "Haftalık Ders Çalışma Süresi": study_hours,
        "Derslerde Dikkat Dağınıklığı Düzeyi": attention,
        "Günlük Kafein Tüketimi": caffeine,
        "Haftalık Spor Yapma Sıklığı": sport_freq,
        "Genel Stres Düzeyi": stress,
        "Uyku Öncesi Telefon Kullanımı": phone_before_sleep,
        "Onay.1": "Kabul Edildi"
    })

df = pd.DataFrame(rows)
df.to_csv("realistic_dummy_buyuk_veri.csv", index=False)
print("✅ Realistic dataset generated: realistic_dummy_buyuk_veri.csv")
