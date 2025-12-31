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
# Lista de servidores espejo para mayor estabilidad
FUENTES_RSS = [
    "https://nitter.net/UnderdogNBA/rss",
    "https://nitter.poast.org/UnderdogNBA/rss",
    "https://nitter.privacydev.net/UnderdogNBA/rss"
]

def monitorear_nba():
    last_guid = "INICIO_PRUEBA" # Forzamos el primer envío para que veas datos YA
    print(">>> Iniciando monitoreo con respaldo multi-fuente...")
    
    while True:
        for url in FUENTES_RSS:
            try:
                print(f">>> Intentando leer: {url}")
                response = requests.get(url, timeout=15)
                if response.status_code == 200:
                    root = ET.fromstring(response.content)
                    item = root.find(".//item")
                    if item is not None:
                        guid = item.find("guid").text
                        titulo = item.find("title").text
                        if guid != last_guid:
                            # ENVÍO A TU APP
                            data = {"jugador_reporte": titulo, "hora": time.ctime()}
                            requests.put(FIREBASE_URL, json=data)
                            print(f">>> ¡ÉXITO! Guardado en Firebase: {titulo}")
                            last_guid = guid
                        break # Si tuvo éxito, sale del bucle de fuentes y espera 60s
            except Exception as e:
                print(f">>> Servidor {url} falló, intentando el siguiente...")
        
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
