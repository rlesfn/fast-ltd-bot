import os
import time
import threading
from flask import Flask
import requests
from datetime import datetime

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")

print(f"Token caricato: {bool(TELEGRAM_BOT_TOKEN)} Chat: {TELEGRAM_CHAT_ID}")

@app.route('/')
def home():
    return "Bot Online! FAST LTD LIVE"

@app.route('/test')
def test():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": "✅ TEST OK! FAST LTD BOT FUNZIONA! Prossimo alert 12:05 / 15:05 / 18:05", "parse_mode": "Markdown"}, timeout=10)
        print(f"Test: {r.status_code} {r.text}")
        return f"Inviato! Status {r.status_code} - Controlla Telegram!"
    except Exception as e:
        return f"Errore: {e}"

def calcola_stat_1T(team_id, is_home=True):
    return {"over05_ht": 85, "over05_ht_home": 75, "over05_ht_away": 70, "media_gol_ht": 1.35, "under25_ht": 80}

def valuta_partita(stats):
    over=stats["over05_ht"]; casa=stats["over05_ht_home"]; ospite=stats["over05_ht_away"]
    media=stats["media_gol_ht"]; under=stats["under25_ht"]; quota=stats["quota_ltd"]
    if over<80 or casa<70 or ospite<65 or not(1.20<=media<=1.80) or not(3.20<=quota<=5.00) or under<60:
        return {"verdetto":"SCARTA"}
    if over>=85 and casa>=75 and ospite>=70 and media>=1.30:
        return {"verdetto":"5 STELLE TOP - ENTRA PESANTE"}
    return {"verdetto":"4 STELLE OK - ENTRA"}

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Errore telegram: {e}")

def main():
    p={"home":"TPV","away":"SalPa","quota_ltd":4.2,"home_id":1234,"away_id":5678,"orario":"17:30"}
    stats={"over05_ht":85,"over05_ht_home":75,"over05_ht_away":70,"media_gol_ht":1.35,"under25_ht":80,"quota_ltd":4.2}
    ris=valuta_partita(stats)
    if "ENTRA" in ris["verdetto"]:
        send_telegram(f"🚀 *FAST LTD 70'* - {p['home']} vs {p['away']} - {ris['verdetto']}")

def scheduler():
    ORARI=[9,12,15,18]
    inviati=set()
    while True:
        now=datetime.now()
        key=f"{now.date()}-{now.hour}"
        if now.hour in ORARI and now.minute<5 and key not in inviati:
            main()
            inviati.add(key)
        time.sleep(60)

threading.Thread(target=scheduler, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
