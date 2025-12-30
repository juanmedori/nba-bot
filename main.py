import requests
import xml.etree.ElementTree as ET
import time

# --- CONFIGURACIÓN ---
# Tu URL de Discord ya está insertada aquí
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1455429847944925227/ErX-EWj4haByOOTUJfXDoZgivPh-fQmaQmho2ee79GCaQtBTYTJt2vEbzeLLwOWs19rp"

# Fuente: Underdog NBA vía Nitter (Gratis y sin API Key)
RSS_URL = "https://nitter.net/Underdog__NBA/rss"

def monitorear_nba():
    last_guid = None
    print("Iniciando monitoreo de @Underdog__NBA en el canal #fantasy...")

    while True:
        try:
            # Consultamos la fuente
            response = requests.get(RSS_URL, timeout=15)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                item = root.find(".//item")
                
                if item is not None:
                    guid = item.find("guid").text
                    titulo = item.find("title").text

                    # Si detectamos un tweet nuevo
                    if guid != last_guid:
                        if last_guid is not None:
                            # Enviamos la notificación a tu Discord
                            payload = {"content": f"🚨 **UNDERDOG NBA:** {titulo}"}
                            requests.post(DISCORD_WEBHOOK_URL, json=payload)
                        last_guid = guid
                        
        except Exception as e:
            print(f"Error de conexión: {e}")
        
        # Esperar 60 segundos antes de la siguiente revisión
        time.sleep(60)

if __name__ == "__main__":
    monitorear_nba()
  
