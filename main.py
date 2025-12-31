import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Bot NBA Multi-Fuente Activo"

# --- CONFIGURACIÓN ---
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/lesiones.json"

# Lista extendida de servidores (si uno falla, prueba el otro)
FUENTES_RSS = [
    "https://nitter.poast.org/UnderdogNBA/rss",
    "https://nitter.net/UnderdogNBA/rss",
    "https://nitter.cz/UnderdogNBA/rss",
    "https://nitter.privacydev.net/UnderdogNBA/rss",
    "https://nitter.moomoo.me/UnderdogNBA/rss"
]

def monitorear_nba():
    last_guid = "FORCE_SEND_FIRST_TIME" 
    print(">>> Iniciando monitoreo con 5 fuentes de respaldo...", flush=True)
    
    while True:
        exito = False
        for url in FUENTES_RSS:
            try:
                print(f">>> Intentando fuente: {url}", flush=True)
                # Timeout corto para no quedarse trabado si el servidor está lento
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200 and len(response.content) > 100:
                    root = ET.fromstring(response.content)
                    item = root.find(".//item")
                    if item is not None:
                        guid = item.find("guid").text
                        titulo = item.find("title").text
                        
                        if guid != last_guid:
                            data = {
                                "jugador_reporte": titulo, 
                                "hora": time.ctime(),
                                "fuente_usada": url
                            }
                            requests.put(FIREBASE_URL, json=data)
                            print(f">>> ¡DATOS ENVIADOS A FIREBASE!: {titulo}", flush=True)
                            last_guid = guid
                        
                        exito = True
                        break # Salimos del bucle 'for' porque ya tuvimos éxito
                else:
                    print(f">>> Fuente {url} respondió vacío o con error.", flush=True)
            except Exception as e:
                print(f">>> Error en {url}: Servidor fuera de servicio.", flush=True)
        
        if not exito:
            print(">>> [AVISO] Ninguna fuente respondió. Reintentando en 60 segundos...", flush=True)
        
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
