import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Historial CBS Player News Activo"

# --- CONFIGURACIÓN ---
FIREBASE_BASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/cbs_player_news"
FIREBASE_POST_URL = f"{FIREBASE_BASE_URL}.json"

# LA FUENTE DE DATOS OFICIAL (Verificada en cbssports.com/rss)
RSS_URL = "https://www.cbssports.com/rss/fantasy/basketball/player-news/"

def limpiar_historial_viejo():
    """Borra noticias que tengan más de 24 horas"""
    try:
        limite_24h = time.time() - (24 * 3600)
        response = requests.get(FIREBASE_POST_URL)
        if response.status_code == 200 and response.json():
            datos = response.json()
            for id_noticia, info in datos.items():
                if info.get('timestamp', 0) < limite_24h:
                    requests.delete(f"{FIREBASE_BASE_URL}/{id_noticia}.json")
                    print(f">>> Limpieza: Borrada noticia antigua.")
    except Exception as e:
        print(f">>> Error en limpieza: {e}")

def monitorear_cbs():
    last_guid = None
    print(">>> Conectando con CBS Player News...")
    
    while True:
        try:
            # Esta URL es estable y no bloquea a Render
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in reversed(items[:10]):
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    
                    if guid != last_guid:
                        # POST guarda como historial (no borra lo anterior)
                        data = {
                            "reporte": titulo,
                            "timestamp": time.time(),
                            "hora": time.ctime()
                        }
                        requests.post(FIREBASE_POST_URL, json=data)
                        print(f">>> NUEVA LESIÓN GUARDADA: {titulo}")
                        last_guid = guid
            
            limpiar_historial_viejo()
        except Exception as e:
            print(f">>> Error: {e}")
        
        time.sleep(180) # Revisa cada 3 minutos

if __name__ == "__main__":
    threading.Thread(target=monitorear_cbs, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
