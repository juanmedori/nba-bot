import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot en Fase de Diagnostico"

# --- CONFIGURACIÓN ---
# Tu URL de Firebase
FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/test_conexion.json"
NOTICIAS_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/lesiones.json"
# Usamos una instancia de Nitter diferente y más estable
RSS_URL = "https://nitter.privacydev.net/UnderdogNBA/rss"

def monitorear_nba():
    print(">>> [PASO 1] Iniciando hilo de monitoreo...", flush=True)
    
    # PRUEBA INICIAL: Enviar algo a Firebase sí o sí
    try:
        print(">>> [PASO 2] Intentando enviar test a Firebase...", flush=True)
        r_test = requests.put(FIREBASE_URL, json={"status": "Bot Conectado", "hora": time.ctime()}, timeout=10)
        print(f">>> [PASO 3] Respuesta de Firebase: {r_test.status_code} (Debe ser 200)", flush=True)
    except Exception as e:
        print(f">>> [ERROR] No se pudo conectar con Firebase: {e}", flush=True)

    last_guid = "PRUEBA_INICIAL"
    
    while True:
        print(">>> [PASO 4] Buscando noticias en Underdog NBA...", flush=True)
        try:
            response = requests.get(RSS_URL, timeout=20)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find(".//item")
                if item is not None:
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    
                    if guid != last_guid:
                        print(f">>> [PASO 5] Nueva noticia detectada: {titulo}", flush=True)
                        data = {
                            "jugador_reporte": titulo,
                            "ultima_actualizacion": time.ctime(),
                            "fuente": "@UnderdogNBA"
                        }
                        requests.put(NOTICIAS_URL, json=data)
                        print(">>> [PASO 6] ¡ÉXITO! Noticia guardada en Firebase.", flush=True)
                        last_guid = guid
            else:
                print(f">>> [AVISO] La fuente de noticias respondió con error {response.status_code}", flush=True)
        except Exception as e:
            print(f">>> [ERROR] Fallo al leer noticias: {e}", flush=True)
        
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
