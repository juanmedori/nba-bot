import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Player News (24h) - Activo"

# --- CONFIGURACIÓN ---
FIREBASE_BASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/historial_jugadores"
FIREBASE_POST_URL = f"{FIREBASE_BASE_URL}.json"

# LA FUENTE CORRECTA: RotoWire NBA (Es la que alimenta la columna lateral de CBS)
RSS_URL = "https://www.rotowire.com/rss/news.php?sport=NBA"

def limpiar_24h():
    """Borra noticias que tengan más de 24 horas"""
    try:
        limite = time.time() - (24 * 3600)
        response = requests.get(FIREBASE_POST_URL)
        if response.status_code == 200 and response.json():
            for id_n, info in response.json().items():
                if info.get('timestamp', 0) < limite:
                    requests.delete(f"{FIREBASE_BASE_URL}/{id_n}.json")
    except Exception as e:
        print(f"[ERROR] Limpieza: {e}", flush=True)

def monitorear_player_news():
    last_guid = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("\n[BOT] >>> INICIANDO CAPTURA DE PLAYER NEWS (24H)", flush=True)
    
    while True:
        try:
            # RotoWire es mucho más estable para los bots que CBS
            response = requests.get(RSS_URL, headers=headers, timeout=20)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                # Procesamos los últimos 15 reportes de jugadores
                for item in reversed(items[:15]): 
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    
                    if guid != last_guid:
                        # Guardamos en la lista acumulada
                        data = {
                            "reporte": titulo,
                            "timestamp": time.time(),
                            "hora": time.ctime()
                        }
                        requests.post(FIREBASE_POST_URL, json=data)
                        print(f"[BOT] >>> NUEVA PLAYER NEWS: {titulo}", flush=True)
                        last_guid = guid
                
                limpiar_24h()
            else:
                print(f"[BOT] >>> Error de fuente (Status {response.status_code})", flush=True)
                
        except Exception as e:
            print(f"[BOT] >>> Error técnico: {e}", flush=True)
        
        # Revisamos cada 3 minutos para capturar todo al instante
        time.sleep(180)

# LANZAMIENTO SEGURO DEL HILO
t = threading.Thread(target=monitorear_player_news, daemon=True)
t.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
