import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Historial NBA Activo"

# --- CONFIGURACIÓN ---
# Usamos un nodo llamado 'historial' para guardar la lista
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/historial.json"
# Feed estable de CBS Sports (NBA Headlines)
RSS_URL = "https://www.cbssports.com/rss/headlines/nba/"

def monitorear_nba():
    last_guid = None
    print(">>> Iniciando recolector de historial...", flush=True)
    
    while True:
        try:
            # CBS no bloquea a Render como lo hace Twitter
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                # Tomamos las últimas noticias del feed
                items = root.findall(".//item")
                
                for item in reversed(items[:10]): # Procesamos las 10 más recientes
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    
                    if guid != last_guid:
                        # Guardamos la noticia con su hora exacta
                        data = {
                            "reporte": titulo,
                            "timestamp": time.time(),
                            "fecha": time.ctime()
                        }
                        # POST añade a la lista sin borrar lo anterior
                        requests.post(FIREBASE_URL, json=data)
                        print(f">>> GUARDADO: {titulo}", flush=True)
                        last_guid = guid
        except Exception as e:
            print(f">>> Error al recolectar: {e}", flush=True)
        
        # Revisa cada 5 minutos para ahorrar recursos
        time.sleep(300)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
