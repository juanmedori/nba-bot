import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Bot NBA: Estructura Gemini Activa"

# --- CONFIGURACIÓN DE FIREBASE ---
BASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com"
# Ruta para el historial de noticias (sugerencia Gemini: 'Tweets/Noticias')
NOTICIAS_URL = f"{BASE_URL}/noticias.json"
# Ruta para el estatus por jugador (sugerencia Gemini: 'Jugadores')
JUGADORES_URL = f"{BASE_URL}/jugadores"

# FUENTE DE DATOS (RotoWire NBA Player News)
RSS_URL = "https://www.rotowire.com/rss/news.php?sport=NBA"

def procesar_reporte_profesional(titulo, descripcion, guid):
    """Organiza la información según la estructura de Gemini"""
    
    # 1. Creamos la entrada para el Historial (Noticias)
    noticia_data = {
        "tweetId": guid,                   # Identificador único
        "contenido": descripcion,          # Texto completo del reporte
        "titulo_corto": titulo,            # Titular rápido
        "fechaPublicacion": time.ctime(),   # Marca de tiempo legible
        "timestamp": time.time(),          # Para la limpieza de 24h
        "categoria": "lesion" if "out" in titulo.lower() or "injur" in titulo.lower() else "noticia"
    }
    
    # Guardamos en noticias (POST crea una lista cronológica)
    requests.post(NOTICIAS_URL, json=noticia_data)

    # 2. Actualizamos o creamos el perfil del Jugador (Estatus Actual)
    # Extraemos el nombre del jugador (suele ser lo primero en el título)
    nombre_jugador = titulo.split(':')[0].strip()
    
    jugador_data = {
        "nombre": nombre_jugador,          #
        "estatusActual": titulo,           # Resumen del estatus
        "ultimaActualizacion": time.ctime() #
    }
    
    # Usamos PATCH para actualizar solo a ese jugador específico sin borrar a los demás
    id_limpio = nombre_jugador.replace(" ", "_").replace(".", "")
    requests.patch(f"{JUGADORES_URL}/{id_limpio}.json", json=jugador_data)
    
    print(f">>> [SISTEMA] Procesado: {nombre_jugador}")

def monitorear_nba():
    last_guid = None
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    while True:
        try:
            response = requests.get(RSS_URL, headers=headers, timeout=20)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                
                for item in reversed(items[:10]):
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    desc = item.find("description").text if item.find("description") is not None else ""
                    
                    if guid != last_guid:
                        procesar_reporte_profesional(titulo, desc, guid)
                        last_guid = guid
            
            # Limpieza opcional: borrar noticias de más de 24h
            ahora = time.time()
            limite = ahora - (24 * 3600)
            historial = requests.get(NOTICIAS_URL).json()
            if historial:
                for id_n, info in historial.items():
                    if info.get('timestamp', 0) < limite:
                        requests.delete(f"{BASE_URL}/noticias/{id_n}.json")

        except Exception as e:
            print(f">>> Error: {e}")
        
        time.sleep(180)

threading.Thread(target=monitorear_nba, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
    
