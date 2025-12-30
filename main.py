import requests
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Prueba Activo"

# --- TU NUEVA URL DE WEBHOOK ---
URL = "https://discord.com/api/webhooks/1455706202494341364/WC-X0B4bVZ3E6EcZgCytv_5R9fNgaCSv5p9SZTCEn1EDocU7D1VNQuLiYdkXFcHNrK5j"

def test_discord():
    print(">>> Intentando enviar mensaje de prueba al nuevo Webhook...")
    try:
        # Esto envía un mensaje directo apenas arranca el servidor
        payload = {"content": "✅ **¡CONEXIÓN EXITOSA!** Si estás leyendo esto, el bot ya está vinculado correctamente a este canal."}
        r = requests.post(URL, json=payload)
        print(f">>> Respuesta de Discord: {r.status_code} (Si es 204, ¡funcionó!)")
    except Exception as e:
        print(f">>> Error al enviar: {e}")

if __name__ == "__main__":
    # Forzamos el envío del mensaje de prueba
    test_discord()
    # Arrancamos la web para Render
    app.run(host='0.0.0.0', port=10000)
