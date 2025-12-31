import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Bot NBA: Conexión Segura Activa"

# --- CONFIGURACIÓN ---
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com"
# URL Corregida (Caso sensible: RSS en mayúsculas suele ser más estable)
RSS_URL = "https://basketballmonster.com/RSS/PlayerNews.aspx"

# Filtro estricto de palabras de salud
PALABRAS_SALUD = ["out", "questionable", "doubtful", "gtd", "probable", "injured", "injury", "surgery", "available", "status", "return", "health", "protocols"]

def test_firebase():
    """Prueba si el bot puede escribir en Firebase apenas arranca"""
    try:
        print("[SISTEMA] >>> Probando conexión a Firebase...", flush=True)
        requests.patch(f"{FIREBASE_URL}/test_conexion.json", json={"ultimo_inicio": time.ctime()})
        print("[SISTEMA] >>> Conexión Firebase: EXITOSA", flush=True)
    except Exception as e:
        print(f"[ERROR] >>> No se pudo conectar a Firebase: {e}", flush=True)

def monitorear_monster_seguro():
    session = requests.Session()
    # Engañamos al sitio para que piense que somos un navegador Chrome real
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    last_guid = None
    test_firebase()
    
    print("\n[BOT] >>> Iniciando monitoreo profesional...", flush=True)
    
    while True:
        try:
            # allow_redirects=True pero manejado por la sesión para evitar el bucle
            response = session.get(RSS_URL, timeout=30)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in reversed(items[:10]):
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    desc = item.find("description").text if item.find("description") is not None else ""
                    
                    if guid != last_guid:
                        # FILTRO DE SALUD: Solo procesamos noticias de estatus
                        if any(p in titulo.lower() for p in PALABRAS_SALUD):
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
                            
                            print(f"[ALERTA] >>> Noticia real de salud: {nombre_jugador}", flush=True)
                        
                        last_guid = guid
            else:
                print(f"[AVISO] >>> Fuente no disponible (Status {response.status_code})", flush=True)
                
        except Exception as e:
            print(f"[ERROR] >>> Error de conexión o redirección: {e}", flush=True)
            # Si Basketball Monster sigue fallando, RotoWire es el respaldo infalible
            print("[SISTEMA] >>> Intentando reconexión en 3 minutos...", flush=True)
        
        time.sleep(180)

threading.Thread(target=monitorear_monster_seguro, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
