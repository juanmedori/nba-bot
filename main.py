import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "NBA Bot Inteligente: Monitoreando Estatus de Salud"

# --- CONFIGURACIÓN ---
# Tu Realtime Database
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com"

# Fuente de datos verificada (RotoWire/CBS Fantasy)
RSS_URL = "https://www.cbssports.com/rss/fantasy/basketball/player-news/"

# FILTRO: Solo guardamos si el título contiene alguna de estas palabras
PALABRAS_SALUD = [
    "out", "questionable", "doubtful", "gtd", "probable", 
    "injured", "injury", "surgery", "return", "health", 
    "protocols", "available", "miss", "status"
]

def limpiar_historial_24h():
    """Borra noticias viejas para mantener Firebase limpio"""
    try:
        limite = time.time() - (24 * 3600)
        resp = requests.get(f"{FIREBASE_URL}/noticias.json")
        if resp.status_code == 200 and resp.json():
            for id_n, info in resp.json().items():
                if info.get('timestamp', 0) < limite:
                    requests.delete(f"{FIREBASE_URL}/noticias/{id_n}.json")
    except Exception as e:
        print(f"Error en limpieza: {e}")

def monitorear_salud_nba():
    last_guid = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    print("\n[SISTEMA] >>> Iniciando Monitoreo con Filtro de Estatus...", flush=True)
    
    while True:
        try:
            response = requests.get(RSS_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                # Revisamos los reportes más recientes
                for item in reversed(items[:15]): 
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    descripcion = item.find("description").text if item.find("description") is not None else ""
                    
                    if guid != last_guid:
                        # --- APLICAMOS EL FILTRO ---
                        if any(palabra in titulo.lower() for palabra in PALABRAS_SALUD):
                            # Estructura sugerida por Gemini en Firebase
                            nombre_jugador = titulo.split(':')[0].strip()
                            
                            # 1. Guardamos en el Feed de Noticias
                            data_noticia = {
                                "tweetId": guid,
                                "contenido": descripcion,
                                "fechaPublicacion": time.ctime(),
                                "timestamp": time.time(),
                                "categoria": "salud"
                            }
                            requests.post(f"{FIREBASE_URL}/noticias.json", json=data_noticia)
                            
                            # 2. Actualizamos el Estatus del Jugador
                            data_jugador = {
                                "nombre": nombre_jugador,
                                "estatusActual": titulo,
                                "ultimaActualizacion": time.ctime()
                            }
                            id_limpio = nombre_jugador.replace(" ", "_").replace(".", "")
                            requests.patch(f"{FIREBASE_URL}/jugadores/{id_limpio}.json", json=data_jugador)
                            
                            print(f"[SISTEMA] >>> ¡ALERTA DE SALUD!: {titulo}", flush=True)
                        
                        last_guid = guid
                
                limpiar_historial_24h()
            else:
                print(f"[AVISO] Fuente no disponible (Status {response.status_code})", flush=True)
                
        except Exception as e:
            print(f"[ERROR] En el bucle: {e}", flush=True)
        
        time.sleep(180) # Revisa cada 3 minutos

# Lanzamos el bot en un hilo separado
threading.Thread(target=monitorear_salud_nba, daemon=True).start()

if __name__ == "__main__":
    # Render requiere que corramos en el puerto 10000
    app.run(host='0.0.0.0', port=10000)
