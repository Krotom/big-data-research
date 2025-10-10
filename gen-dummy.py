import pandas as pd
import random
from datetime import datetime, timedelta

# --- Configuration ---
n = 30

def random_time(start="22:00", end="08:00"):
    """Generate random time string between given hours"""
    fmt = "%H:%M"
    start_t = datetime.strptime(start, fmt)
    end_t = datetime.strptime(end, fmt)
    delta = (end_t - start_t).seconds
    rand = random.randint(0, delta)
    return (start_t + timedelta(seconds=rand)).strftime(fmt)

def random_multi(options, min_n=1, max_n=3):
    return "\n".join(random.sample(options, random.randint(min_n, max_n)))

platforms = [
    "Instagram", "TikTok", "YouTube", "Snapchat", "Facebook",
    "X (Twitter)", "Reddit", "Discord", "Pinterest", "LinkedIn", "Twitch"
]
purposes = ["Sosyal Medya", "Oyun", "Eğitim", "Video / Film İzleme", "Spor"]

rows = []
for _ in range(n):
    gender = random.choice(["ERKEK", "KIZ"])
    age = random.randint(13, 18)
    grade = random.choice(["Hazırlık", "9", "10", "11", "12"])
    school = random.choice(["DEVLET", "ÖZEL"])
    sleep_avg = round(random.uniform(6, 10), 1)
    weekday_sleep = random_time("21:00", "00:00")
    weekday_wake = random_time("06:00", "09:00")
    weekend_sleep = random_time("22:00", "01:00")
    weekend_wake = random_time("08:00", "11:00")
    sleep_diff = random.randint(1, 5)
    snooze = random.randint(1, 5)
    academic_sat = random.randint(1, 5)
    sleep_quality = random.randint(3, 10)
    tired_morning = random.randint(1, 5)
    screen_time = random.randint(1, 7)
    used_platforms = random_multi(platforms, 2, 5)
    usage_purpose = random_multi(purposes, 1, 3)
    gpa = random.randint(60, 100)
    lgs = random.randint(250, 480)
    study_hours = random.randint(2, 20)
    attention = random.randint(1, 5)
    caffeine = random.randint(0, 3)
    sport_freq = random.randint(0, 7)
    stress = random.randint(1, 5)
    phone_before_sleep = random.randint(5, 90)
    
    rows.append({
        "Submission Date": "Eki 9, 2025",
        "Onay": "Kabul Edildi",
        "Cinsiyet": gender,
        "Yaş": age,
        "Sınıf Seviyesi": grade,
        "Okul Türü": school,
        "Ortalama Uyku Süresi": sleep_avg,
        "Hafta İçi Uyuma Saati": weekday_sleep,
        "Hafta İçi Uyanma Saati": weekday_wake,
        "Hafta Sonu Uyuma Saati": weekend_sleep,
        "Hafta Sonu Uyanma Saati": weekend_wake,
        "Uykuya Dalmada Zorluk Düzeyi": sleep_diff,
        "Sabahları Alarm Erteleme Düzeyi": snooze,
        "Akademik Başarı Memnuniyeti": academic_sat,
        "Uyku Kalitesi": sleep_quality,
        "Sabah Yorgun Uyanma Düzeyi": tired_morning,
        "Günlük Ekran Kullanım Süresi": screen_time,
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
df.to_csv("dummy_buyuk_veri.csv", index=False)
print("✅ Dummy dataset created: dummy_buyuk_veri.csv")
