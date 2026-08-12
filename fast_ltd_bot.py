import os
import time
import threading
from flask import Flask
import requests
from datetime import datetime

app = Flask(__name__)

# LEGGE QUALSIASI NOME CHE HAI MESSO SU RENDER
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN") or ""
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID") or ""

# PULISCE IL TOKEN SE HAI SCRITTO FRASE PRIMA
if "8744" in TELEGRAM_BOT_TOKEN:
    # estrae solo il token vero che inizia con 8744
    start = TELEGRAM_BOT_TOKEN.find("8744")
    TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN[start:].strip()

print(f"Token caricato: {bool(TELEGRAM_BOT_TOKEN)} Chat: {TELEGRAM_CHAT_ID}")

@app.route('/')
def home():
    return "Bot Online! FAST LTD LIVE - Token OK" if TELEGRAM_BOT_TOKEN else "Token MANCANTE!"

@app.route('/test')
def test():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": "✅ TEST OK! FAST LTD BOT FUNZIONA! Ora sei a posto!", "parse_mode": "Markdown"}, timeout=10)
        return f"Status Telegram: {r.status_code} - {r.text} - Controlla Telegram!"
    except Exception as e:
        return f"Errore: {e}"

def scheduler():
    ORARI=[9,12,15,18]
    inviati=set()
    while True:
        now=datetime.now()
        key=f"{now.date()}-{now.hour}"
        if now.hour in ORARI and now.minute<5 and key not in inviati:
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": f"🚀 FAST LTD 70' - Check ore {now.hour}:00"}, timeout=10)
                inviati.add(key)
            except: pass
        time.sleep(60)

threading.Thread(target=scheduler, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
