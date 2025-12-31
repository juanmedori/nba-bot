import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot CBS Player News: Activo y Monitoreando"

# --- CONFIGURACIÓN ---
FIREBASE_BASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/cbs_player_news"
FIREBASE_POST_URL = f"{FIREBASE_BASE_URL}.json"
RSS_URL = "https://www.cbssports.com/rss/fantasy/basketball/player-news/"

def monitorear_cbs_firme():
    last_guid = "PRIMERA_CORRIDA_DEBUG" # Forzamos el primer envío
    # Identidad de navegador para asegurar que CBS nos responda
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    
    print("\n[SISTEMA] >>> MOTOR DE NOTICIAS INICIADO", flush=True)
    
    while True:
        try:
            print(f"[SISTEMA] >>> Buscando en CBS Player News...", flush=True)
            response = requests.get(RSS_URL, headers=headers, timeout=20)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                if not items:
                    print("[SISTEMA] >>> Aviso: Feed de CBS vacío momentáneamente.", flush=True)
                
                for item in reversed(items[:10]):
                    guid = item.find("guid").text if item.find("guid") is not None else item.find("link").text
                    titulo = item.find("title").text
                    
                    if guid != last_guid:
                        data = {
                            "reporte": titulo,
                            "timestamp": time.time(),
                            "hora_reporte": time.ctime(),
                            "id": guid
                        }
                        # Enviamos a Firebase
                        requests.post(FIREBASE_POST_URL, json=data)
                        print(f"[SISTEMA] >>> ¡ÉXITO! Guardado: {titulo}", flush=True)
                        last_guid = guid
            else:
                print(f"[SISTEMA] >>> Error de fuente (Status {response.status_code})", flush=True)
                
        except Exception as e:
            print(f"[SISTEMA] >>> Error crítico en el bucle: {e}", flush=True)
        
        time.sleep(180)

# ESTO ASEGURA QUE EL BOT ARRANQUE EN RENDER SIEMPRE
print("[SISTEMA] >>> Lanzando hilo de monitoreo global...", flush=True)
threading.Thread(target=monitorear_cbs_firme, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
