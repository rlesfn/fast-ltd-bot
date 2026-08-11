"""
FAST - ALGORITMO LTD 70' - BOT AUTOMATICO
Obiettivo: trova partite con gol 1T 15'-35' per LTD fino max 70'

Logica 100% fedele allo schema foto:
Sezione 1: Filtri obbligatori ultime 10
Sezione 2: Valutazione stelle
Sezione 3: Gestione LTD
"""

import requests
from datetime import datetime

# CONFIG
TELEGRAM_BOT_TOKEN = "INSERISCI_QUI_TOKEN"
TELEGRAM_CHAT_ID = "INSERISCI_QUI_CHAT_ID"
API_FOOTBALL_KEY = "INSERISCI_QUI_API_FOOTBALL_KEY"
BETFAIR_APP_KEY = "INSERISCI_QUI_BETFAIR"

# FILTRI OBBLIGATORI - SEZIONE 1
FILTRO_OVER_05_HT = 80
FILTRO_CASA = 70
FILTRO_OSPITE = 65
FILTRO_MEDIA_MIN = 1.20
FILTRO_MEDIA_MAX = 1.80
FILTRO_QUOTA_MIN = 3.20
FILTRO_QUOTA_MAX = 5.00
FILTRO_UNDER_25_HT = 60

def calcola_stat_1T(team_id, is_home=True, api_key=API_FOOTBALL_KEY):
    """Recupera ultime 10 partite e calcola stats 1T - usa API-Football"""
    # Endpoint esempio - da adattare a API-Football v3
    # GET /fixtures?team={team_id}&last=10
    # Per ogni fixture: estrai halftime score
    # Questo è lo scheletro - implementazione reale richiede parsing
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
    headers = {"x-apisports-key": api_key}
    # r = requests.get(url, headers=headers)
    # ... parsing ...
    # Mock per demo - sostituire con dati reali
    return {
        "over05_ht": 85,
        "over05_ht_home": 75,
        "over05_ht_away": 70,
        "media_gol_ht": 1.35,
        "under25_ht": 80
    }

def valuta_partita(stats):
    """SEZIONE 2 - VALUTAZIONE"""
    over = stats["over05_ht"]
    casa = stats["over05_ht_home"]
    ospite = stats["over05_ht_away"]
    media = stats["media_gol_ht"]
    under = stats["under25_ht"]
    quota = stats["quota_ltd"]

    # Filtri obbligatori
    if over < 80: return {"verdetto": "SCARTA", "motivo": f"Over 0.5 1T {over}% <80%"}
    if casa < 70: return {"verdetto": "SCARTA", "motivo": f"Casa {casa}% <70%"}
    if ospite < 65: return {"verdetto": "SCARTA", "motivo": f"Ospite {ospite}% <65%"}
    if not (1.20 <= media <= 1.80): return {"verdetto": "SCARTA", "motivo": f"Media {media} fuori 1.20-1.80"}
    if not (3.20 <= quota <= 5.00): return {"verdetto": "SCARTA", "motivo": f"Quota LTD {quota} fuori range"}
    if under < 60: return {"verdetto": "SCARTA", "motivo": f"Under 2.5 1T {under}% <60%"}

    # Stelle
    if over >= 85 and casa >= 75 and ospite >= 70 and media >= 1.30:
        return {"verdetto": "5 STELLE TOP - ENTRA PESANTE", "stelle": 5}
    elif 80 <= over <= 84 and casa >= 70 and ospite >= 65:
        return {"verdetto": "4 STELLE OK - ENTRA", "stelle": 4}
    else:
        return {"verdetto": "SCARTA - SOTTO SOGLIA", "stelle": 0}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def main():
    # Esempio: lista partite da Betfair Exchange
    # In produzione: chiamata a Betfair API per lista eventi del giorno con quota LTD 3.20-5.00
    partite_oggi = [
        {"home": "TPV", "away": "SalPa", "quota_ltd": 4.2, "home_id": 1234, "away_id": 5678, "orario": "17:30"},
        {"home": "Slovan Bratislava", "away": "Mjallby", "quota_ltd": 3.75, "home_id": 111, "away_id": 222, "orario": "20:15"},
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
            msg = f"""🚀 *FAST LTD 70' - SEGNALE*

{p['orario']} - {p['home']} vs {p['away']}
Quota LTD: {p['quota_ltd']}

📊 STATS 1T (ultime 10):
Over 0.5 1T: {stats_combinate['over05_ht']:.0f}% ✅
Casa: {stats_combinate['over05_ht_home']:.0f}% 
Ospite: {stats_combinate['over05_ht_away']:.0f}%
Media Gol 1T: {stats_combinate['media_gol_ht']:.2f}
Under 2.5 1T: {stats_combinate['under25_ht']:.0f}%

{risultato['verdetto']}

⚙️ GESTIONE:
• Ingresso pre-match 3.20-5.00
• Segui ritmo 1T
• Se gol 15-35' gestisci profitto
• USCITA MAX 70' MAI OLTRE
"""
            print(msg)
            # send_telegram(msg)

if __name__ == "__main__":
    main()
