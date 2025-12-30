import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

# Esto es solo para que Render no falle
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot NBA Activo"

# CONFIGURACIÓN
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455429847944925227/ErX-EWj4haByOOTUJfXDoZgivPh-fQmaQmho2ee79GCaQtBTYTJt2vEbzeLLwOWs19rp"
RSS_URL = "https://nitter.net/UnderdogNBA/rss"

def monitorear_nba():
    last_guid = None
    # PRUEBA: Esto debe llegar a tu Discord en 2 minutos
    requests.post(DISCORD_WEBHOOK_URL, json={"content": "🚀 **Bot de NBA Conectado:** Probando sistema por primera vez hoy."})
    
    while True:
        try:
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find(".//item")
                if item is not None:
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    if guid != last_guid:
                        if last_guid is not None:
                            requests.post(DISCORD_WEBHOOK_URL, json={"content": f"🚨 **ALERTA:** {titulo}"})
                        last_guid = guid
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
