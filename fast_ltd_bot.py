import os
import time
import threading
from flask import Flask
import requests
from datetime import datetime

app = Flask(__name__)

# --- PRENDE I TOKEN DA RENDER (non dalle scritte) ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
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
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": "✅ TEST OK! FAST LTD BOT FUNZIONA! Prossimo alert alle 12:05 / 15:05 / 18:05", "parse_mode": "Markdown"}, timeout=10)
        print(f"Test telegram status: {r.status_code} {r.text}")
        return f"Test inviato! Status: {r.status_code} - Controlla Telegram!"
    except Exception as e:
        return f"Errore test: {e}"

# --- IL TUO ALGORITMO FAST LTD (uguale) ---
def calcola_stat_1T(team_id, is_home=True):
    return {
        "over05_ht": 85, "over05_ht_home": 75, "over05_ht_away": 70,
        "media_gol_ht": 1.35, "under25_ht": 80
    }

def valuta_partita(stats):
    over = stats["over05_ht"]; casa = stats["over05_ht_home"]; ospite = stats["over05_ht_away"]
    media = stats["media_gol_ht"]; under = stats["under25_ht"]; quota = stats["quota_ltd"]
    if over < 80: return {"verdetto": "SCARTA"}
    if casa < 70: return {"verdetto": "SCARTA"}
    if ospite < 65: return {"verdetto": "SCARTA"}
    if not (1.20 <= media <= 1.80): return {"verdetto": "SCARTA"}
    if not (3.20 <= quota <= 5.00): return {"verdetto": "SCARTA"}
    if under < 60: return {"verdetto": "SCARTA"}
    if over >= 85 and casa >= 75 and ospite >= 70 and media >= 1.30:
        return {"verdetto": "5 STELLE TOP - ENTRA PESANTE", "stelle": 5}
    elif 80 <= over <= 84 and casa >= 70 and ospite >= 65:
        return {"verdetto": "4 STELLE OK - ENTRA", "stelle": 4}
    else:
        return {"verdetto": "SCARTA", "stelle": 0}

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Errore telegram: {e}")

def main():
    partite_oggi = [
        {"home": "TPV", "away": "SalPa", "quota_ltd": 4.2, "home_id": 1234, "away_id": 5678, "orario": "17:30"},
    ]
    for p in partite_oggi:
        stats_home = calcola_stat_1T(p["home_id"], True)
        stats_away = calcola_stat_1T(p["away_id"], False)
        stats_combinate = {
            "over05_ht": (stats_home["over05_ht"] + stats_away["over05_ht"]) / 2,
            "over05_ht_home": stats_home["over05_ht_home"],
            "over05_ht_away": stats_away["over05_ht_away"],
            "media_gol_ht": (stats_home["media_gol_ht"] + stats_away["media_gol_ht"]) / 2,
            "under25_ht": (stats_home["under25_ht"] + stats_away["under25_ht"]) / 2,
            "quota_ltd": p["quota_ltd"]
        }
        risultato = valuta_partita(stats_combinate)
        if "ENTRA" in risultato["verdetto"]:
            msg = f"🚀 *FAST LTD 70'*\n{p['orario']} - {p['home']} vs {p['away']}\n{risultato['verdetto']}"
            send_telegram(msg)

# --- SCHEDULER ---
def scheduler():
    ORARI = [9, 12, 15, 18]
    inviati = set()
    while True:
        now = datetime.now()
        ora = now.hour
        key = f"{now.date()}-{ora}"
        if ora in ORARI and now.minute < 5 and key not in inviati:
            print(f"Sono le {ora}:00 - mando segnali!")
            main()
            inviati.add(key)
        time.sleep(60)

threading.Thread(target=scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
