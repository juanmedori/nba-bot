import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Historial CBS Player News 24h Activo"

# --- CONFIGURACIÓN ---
# Carpeta donde se guardará la lista de reportes en Firebase
FIREBASE_BASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/cbs_player_news"
FIREBASE_POST_URL = f"{FIREBASE_BASE_URL}.json"

# --- LA FUENTE CORRECTA ---
# Este es el RSS específico para la sección "Player News" de CBS Fantasy
RSS_URL = "https://www.cbssports.com/rss/fantasy/basketball/player-news/"

def limpiar_historial_viejo():
    """Borra reportes con más de 24 horas de antigüedad"""
    try:
        ahora = time.time()
        # 24 horas * 60 minutos * 60 segundos
        limite_24h = ahora - (24 * 3600)
        
        # Leemos todo el historial actual
        response = requests.get(FIREBASE_POST_URL)
        if response.status_code == 200 and response.json():
            datos = response.json()
            # Revisamos cada noticia guardada
            for id_noticia, info in datos.items():
                # Si el timestamp es más viejo que el límite de 24h, lo borramos
                if info.get('timestamp', 0) < limite_24h:
                    requests.delete(f"{FIREBASE_BASE_URL}/{id_noticia}.json")
                    print(f">>> Limpieza: Borrada noticia antigua {id_noticia}")
    except Exception as e:
        print(f">>> Error durante la limpieza automática: {e}")

def monitorear_cbs_player_news():
    last_guid = None
    print(">>> Iniciando capturador de CBS Player News (Historial 24h)...", flush=True)
    
    while True:
        try:
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                # Revisamos los últimos 10 reportes (de más viejo a más nuevo)
                for item in reversed(items[:10]): 
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    # CBS a veces pone la descripción del reporte en la etiqueta 'description'
                    descripcion = item.find("description").text if item.find("description") is not None else ""
                    
                    if guid != last_guid:
                        # Creamos el objeto de la noticia
                        data = {
                            "titulo": titulo,
                            "detalle": descripcion, # El texto completo del reporte
                            "timestamp": time.time(), # Para saber cuándo borrarla
                            "hora_legible": time.ctime(),
                            "fuente": "CBS Player News"
                        }
                        # Usamos POST para añadir a la lista en Firebase
                        requests.post(FIREBASE_POST_URL, json=data)
                        print(f">>> NUEVO REPORTE CBS GUARDADO: {titulo}", flush=True)
                        last_guid = guid
            
            # Ejecutamos la limpieza en cada ciclo
            limpiar_historial_viejo()
            
        except Exception as e:
            print(f">>> Error de conexión con CBS: {e}", flush=True)
        
        # Revisamos cada 3 minutos
        time.sleep(180)

if __name__ == "__main__":
    threading.Thread(target=monitorear_cbs_player_news, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
