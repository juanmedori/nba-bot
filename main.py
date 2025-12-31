import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "NBA Status Bot: Solo Lesiones y Altas/Bajas"

# --- CONFIGURACIÓN ---
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com"
# Cambiamos a RotoWire porque CBS está dando 404 en tus logs
RSS_URL = "https://www.rotowire.com/rss/news.php?sport=NBA"

# FILTRO ESTRICTO: Solo si tiene estas palabras es un cambio de estatus
PALABRAS_ESTATUS = [
    "out", "questionable", "doubtful", "gtd", "probable", 
    "injured", "injury", "surgery", "available", "status", 
    "protocols", "return", "missing", "gametime"
]

def monitorear_estatus_limpio():
    last_guid = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("\n[SISTEMA] >>> Conectando a fuente estable...", flush=True)
    
    while True:
        try:
            response = requests.get(RSS_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in reversed(items[:15]):
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    desc = item.find("description").text if item.find("description") is not None else ""
                    
                    if guid != last_guid:
                        # --- EL FILTRO DE ACERO ---
                        # Solo procesamos si el título tiene una palabra de lesión o estatus
                        if any(p in titulo.lower() for p in PALABRAS_ESTATUS):
                            nombre_jugador = titulo.split(':')[0].strip()
                            
                            # 1. Guardar en carpeta 'noticias' (Historial 24h)
                            noticia_data = {
                                "tweetId": guid,
                                "contenido": desc,
                                "timestamp": time.time(),
                                "hora": time.ctime()
                            }
                            requests.post(f"{FIREBASE_URL}/noticias.json", json=noticia_data)
                            
                            # 2. Guardar en carpeta 'jugadores' (Estatus Actual)
                            jugador_id = nombre_jugador.replace(" ", "_").replace(".", "")
                            estatus_data = {
                                "nombre": nombre_jugador,
                                "estatus": titulo,
                                "ultima_actualizacion": time.ctime()
                            }
                            requests.patch(f"{FIREBASE_URL}/jugadores/{jugador_id}.json", json=estatus_data)
                            
                            print(f"[EXITO] >>> Guardado estatus real: {nombre_jugador}", flush=True)
                        
                        last_guid = guid
            else:
                print(f"[ERROR] >>> Fuente no responde (Status {response.status_code})", flush=True)
                
        except Exception as e:
            print(f"[ERROR] >>> Técnico: {e}", flush=True)
        
        time.sleep(180) # Revisa cada 3 minutos

threading.Thread(target=monitorear_estatus_limpio, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
