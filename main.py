import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Bot NBA: Fuente Basketball Monster Activa"

# --- CONFIGURACIÓN ---
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com"
# La versión RSS de la página que encontraste (mejor para bots)
RSS_URL = "https://basketballmonster.com/rss/playernews.aspx"

def monitorear_monster_nba():
    last_guid = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("\n[SISTEMA] >>> Conectando a Basketball Monster...", flush=True)
    
    while True:
        try:
            response = requests.get(RSS_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in reversed(items[:10]):
                    guid = item.find("guid").text
                    titulo = item.find("title").text # Ej: "Josh Giddey (Hamstring) is out"
                    desc = item.find("description").text if item.find("description") is not None else ""
                    
                    if guid != last_guid:
                        # Extraemos el nombre antes del paréntesis
                        nombre_jugador = titulo.split('(')[0].strip() if '(' in titulo else titulo.split(':')[0].strip()
                        
                        # 1. Carpeta 'noticias': Historial sugerido por Gemini
                        noticia = {
                            "tweetId": guid,
                            "contenido": desc,
                            "timestamp": time.time(),
                            "fecha": time.ctime()
                        }
                        requests.post(f"{FIREBASE_URL}/noticias.json", json=noticia)
                        
                        # 2. Carpeta 'jugadores': Estatus actual
                        jugador_id = nombre_jugador.replace(" ", "_").replace(".", "")
                        estatus = {
                            "nombre": nombre_jugador,
                            "estatusActual": titulo,
                            "ultimaActualizacion": time.ctime()
                        }
                        requests.patch(f"{FIREBASE_URL}/jugadores/{jugador_id}.json", json=estatus)
                        
                        print(f"[EXITO] >>> Reporte procesado: {nombre_jugador}", flush=True)
                        last_guid = guid
            else:
                print(f"[AVISO] >>> Error de conexión: {response.status_code}", flush=True)
                
        except Exception as e:
            print(f"[ERROR] >>> Fallo técnico: {e}", flush=True)
        
        time.sleep(180) # Revisa cada 3 minutos

threading.Thread(target=monitorear_monster_nba, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
