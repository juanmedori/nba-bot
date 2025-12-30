import requests
import xml.etree.ElementTree as ET
import time
import threading
from flask import Flask
import sys

# --- WEB PARA RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot NBA Activo y Vigilando"

# --- CONFIGURACIÓN ---
# Tu NUEVA URL de Webhook confirmada
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455706202494341364/WC-X0B4bVZ3E6EcZgCytv_5R9fNgaCSv5p9SZTCEn1EDocU7D1VNQuLiYdkXFcHNrK5j"
# Cuenta de tu foto: UnderdogNBA
RSS_URL = "https://nitter.net/UnderdogNBA/rss"

def monitorear_nba():
    last_guid = None
    print(">>> Iniciando hilo de monitoreo...", flush=True)
    
    # Mensaje de arranque para confirmar conexión en Discord
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": "🏀 **¡Sistema de Alertas Conectado!** Estoy vigilando a @UnderdogNBA para tu app."})
        print(">>> Mensaje de bienvenida enviado a Discord.", flush=True)
    except Exception as e:
        print(f">>> Error al enviar a Discord: {e}", flush=True)
    
    while True:
        try:
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find(".//item")
                if item is not None:
                    guid = item.find("guid").text
                    titulo = item.find("title").text
                    if guid != last_guid:
                        if last_guid is not None:
                            # Aquí es donde ocurre la magia de la notificación
                            requests.post(DISCORD_WEBHOOK_URL, json={"content": f"🚨 **ALERTA NBA:** {titulo}"})
                            print(f">>> Noticia enviada: {titulo}", flush=True)
                        last_guid = guid
        except Exception as e:
            print(f">>> Error de conexión: {e}", flush=True)
        # Revisa cada 60 segundos
        time.sleep(60)

if __name__ == "__main__":
    # Arrancar el monitoreo en un hilo separado
    threading.Thread(target=monitorear_nba, daemon=True).start()
    # Arrancar Flask para Render
    print(">>> Servidor Flask arrancando...", flush=True)
    app.run(host='0.0.0.0', port=10000)
