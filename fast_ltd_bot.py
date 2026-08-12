import os, time, threading, requests
from flask import Flask
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = (os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
CHAT_ID = (os.environ.get("CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID") or "")
API_KEY = (os.environ.get("API_FOOTBALL_KEY") or "").strip()
if "8744" in BOT_TOKEN: BOT_TOKEN = BOT_TOKEN[BOT_TOKEN.find("8744"):].strip()

HEADERS = {"x-apisports-key": API_KEY}
CACHE = {}

@app.route('/')
def home():
    return f"BOT WORLD LIVE! API KEY: {bool(API_KEY)} - ORE 12:00 ONLY - FIXED!"

@app.route('/test')
def test():
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": "✅ TEST OK BOT WORLD ORE 12!"})
    return "Test inviato!"

@app.route('/test-scan')
def test_scan():
    threading.Thread(target=main_scan, daemon=True).start()
    return "Scansione avviata! Guarda Telegram tra 1 min!"

def get_stats(team_id, is_home):
    if team_id in CACHE and datetime.now() - CACHE[team_id]['time'] < timedelta(hours=12):
        return CACHE[team_id]['data']
    try:
        r = requests.get(f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10", headers=HEADERS, timeout=15).json()
        fixtures = r.get('response', [])
        if not fixtures: return None
        over=0; media_list=[]; under=0; spec=0; cnt_spec=0
        for f in fixtures:
            hh = f['score']['halftime']['home']; ha = f['score']['halftime']['away']
            if hh is None: continue
            tot = hh+ha
            if tot>=1: over+=1
            if tot<=2: under+=1
            media_list.append(tot)
            if is_home and f['teams']['home']['id']==team_id and tot>=1: spec+=1
            if not is_home and f['teams']['away']['id']==team_id and tot>=1: spec+=1
            if (is_home and f['teams']['home']['id']==team_id) or (not is_home and f['teams']['away']['id']==team_id):
                cnt_spec+=1
        tot=len(media_list) or 1
        stats={"over":over/tot*100,"media":sum(media_list)/tot if media_list else 0,"under":under/tot*100,"spec":spec/max(1,cnt_spec)*100}
        CACHE[team_id]={'data':stats,'time':datetime.now()}
        return stats
    except: return None

def send(m):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":m,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def main_scan():
    if not API_KEY: send("⚠ API_FOOTBALL_KEY mancante!"); return
    today=datetime.now().strftime("%Y-%m-%d")
    try:
        res=requests.get(f"https://v3.football.api-sports.io/fixtures?date={today}", headers=HEADERS, timeout=15).json()
        partite=res.get('response', [])[:50]
        send(f"🔍 Avvio scansione {today}: {len(partite)} partite trovate (WORLD) - ORE 12")
        for f in partite:
            hid=f['teams']['home']['id']; aid=f['teams']['away']['id']
            sh=get_stats(hid,True); time.sleep(0.35)
            sa=get_stats(aid,False); time.sleep(0.35)
            if not sh or not sa: continue
            over=(sh['over']+sa['over'])/2; media=(sh['media']+sa['media'])/2; under=(sh['under']+sa['under'])/2
            if over<80 or sh['spec']<70 or sa['spec']<65 or not(1.2<=media<=1.8) or under<60: continue
            verdetto="5 STELLE TOP 💣" if over>=85 and sh['spec']>=75 and sa['spec']>=70 else "4 STELLE OK ✅"
            msg=f"🚀 *FAST LTD {verdetto}*\n🕒 {f['fixture']['date'][11:16]} {f['teams']['home']['name']} vs {f['teams']['away']['name']}\n🏆 {f['league']['name']}\nOver 0.5 1T: {over:.0f}% Casa:{sh['spec']:.0f}% Osp:{sa['spec']:.0f}% Media:{media:.2f}"
            send(msg)
        send(f"✅ Fine scansione WORLD {today} - Prossima domani ore 12")
    except Exception as e: send(f"❌ Errore: {e}")

def scheduler():
    sent=set()
    while True:
        now=datetime.now()
        for h in [12]:
            key=f"{now.date()}-{h}"
            if now.hour==h and now.minute<5 and key not in sent:
                main_scan()
                sent.add(key)
        time.sleep(60)

threading.Thread(target=scheduler,daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
