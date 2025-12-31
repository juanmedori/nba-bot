import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Bot NBA: Bypass Activo"

# --- CONFIGURACIÓN ---
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/lesiones.json"

# Usamos el Proxy de Google para esconder a Render
def google_proxy(url):
    return f"https://images1-focus-opensocial.googleusercontent.com/gadgets/proxy?container=focus&refresh=60&url={url}"

FUENTES_RSS = [
    google_proxy("https://nitter.poast.org/UnderdogNBA/rss"),
    google_proxy("https://nitter.net/UnderdogNBA/rss"),
    "https://nitter.unixfox.eu/UnderdogNBA/rss", # Fuente directa de respaldo
    "https://nitter.perennialte.ch/UnderdogNBA/rss"
]

def monitorear_nba():
    last_guid = "FORCE_START_001"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    
    print(">>> Iniciando monitoreo con Bypass de Google...", flush=True)
    
    while True:
        exito_ronda = False
        for url in FUENTES_RSS:
            try:
                print(f">>> Intentando con: {url[:50]}...", flush=True)
                response = requests.get(url, headers=headers, timeout=20)
                
                # Si Google nos devuelve un 200, tenemos la noticia
                if response.status_code == 200 and len(response.content) > 300:
                    root = ET.fromstring(response.content)
                    item = root.find(".//item")
                    if item is not None:
                        guid = item.find("guid").text
                        titulo = item.find("title").text
                        
                        if guid != last_guid:
                            # ENVÍO INMEDIATO A FIREBASE
                            res = requests.put(FIREBASE_URL, json={
                                "jugador_reporte": titulo,
                                "hora": time.ctime(),
                                "estado": "ACTUALIZADO"
                            })
                            print(f">>> ¡CONEXIÓN ROMPIÓ EL BLOQUEO!: {titulo}", flush=True)
                            last_guid = guid
                        
                        exito_ronda = True
                        break
                else:
                    print(f">>> Fuente no disponible (Status {response.status_code})", flush=True)
            except Exception as e:
                print(f">>> Error en esta fuente, probando la siguiente...", flush=True)
        
        if not exito_ronda:
            print(">>> [ALERTA] Nitter sigue bloqueando incluso con Proxy. Reintentando en 60s...", flush=True)
        
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
