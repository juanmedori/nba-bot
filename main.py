import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de NBA Conectado a Firebase"

# --- CONFIGURACIÓN ---
# Tu URL de Firebase con la extensión .json necesaria para la conexión
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/lesiones.json"
# Usamos el servidor más estable de Nitter
RSS_URL = "https://nitter.poast.org/UnderdogNBA/rss"

def monitorear_nba():
    # Cambia last_guid = None por esto:
    last_guid = "PRUEBA_INICIAL" 
    print(">>> Forzando primer envío a Firebase...")
    
    while True:
        try:
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find(".//item")
                if item is not None:
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    
                    # Al ser last_guid distinto a guid, enviará el último tweet de inmediato
                    if guid != last_guid:
                        data = {
                            "jugador_reporte": titulo,
                            "ultima_actualizacion": time.ctime(),
                            "fuente": "@UnderdogNBA"
                        }
                        requests.put(FIREBASE_URL, json=data)
                        print(f">>> ÉXITO: {titulo} guardado.")
                        last_guid = guid
        except Exception as e:
            print(f">>> Error de sincronización: {e}")
        
        # Revisa cada 60 segundos
        time.sleep(60)

if __name__ == "__main__":
    # Arranca el motor en segundo plano
    threading.Thread(target=monitorear_nba, daemon=True).start()
    # Mantiene vivo el servidor para Render
    app.run(host='0.0.0.0', port=10000)
