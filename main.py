import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Bot NBA con Identidad Real Activo"

FIREBASE_URL = "https://nba-injuries-app-default-rtdb.firebaseio.com/lesiones.json"

# Fuentes actualizadas y un par nuevas más estables
FUENTES_RSS = [
    "https://nitter.poast.org/UnderdogNBA/rss",
    "https://nitter.net/UnderdogNBA/rss",
    "https://nitter.perennialte.ch/UnderdogNBA/rss",
    "https://nitter.esmailelbob.xyz/UnderdogNBA/rss"
]

def monitorear_nba():
    last_guid = "FORZAR_PRIMER_ENVIO"
    # Esta línea es la clave: le dice a Nitter que somos un usuario real
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    print(">>> Iniciando monitoreo con camuflaje de navegador...", flush=True)
    
    while True:
        exito = False
        for url in FUENTES_RSS:
            try:
                print(f">>> Intentando leer con camuflaje: {url}", flush=True)
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200 and len(response.content) > 200:
                    root = ET.fromstring(response.content)
                    item = root.find(".//item")
                    if item is not None:
                        guid = item.find("guid").text
                        titulo = item.find("title").text
                        
                        if guid != last_guid:
                            data = {"jugador_reporte": titulo, "hora": time.ctime()}
                            requests.put(FIREBASE_URL, json=data)
                            print(f">>> ¡ÉXITO TOTAL!: {titulo} enviado a Firebase", flush=True)
                            last_guid = guid
                        
                        exito = True
                        break
                else:
                    print(f">>> Fuente {url} bloqueada o vacía (Status: {response.status_code})", flush=True)
            except Exception as e:
                print(f">>> Error técnico en {url}: {e}", flush=True)
        
        if not exito:
            print(">>> [AVISO] Nitter sigue bloqueando. Reintentando en 60s...", flush=True)
        
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=monitorear_nba, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
