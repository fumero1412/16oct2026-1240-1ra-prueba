from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import asyncio
import os
import logging
import threading
from flask import Flask

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING")
CANAL_ORIGEN = os.environ.get("CANAL_ORIGEN", "Horny_J")
GRUPO_DESTINO = int(os.environ.get("GRUPO_DESTINO", "-1003764262854"))
TOPIC_ID = int(os.environ.get("TOPIC_ID", "752598"))

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Replicacion en Ejecucion."

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

threading.Thread(target=run_flask, daemon=True).start()
logging.info("Flask iniciado en 8080")

async def cargar_progreso(client):
    try:
        logging.info("Buscando progreso guardado...")
        async for m in client.iter_messages('me', limit=20):
            if m.text and m.text.startswith("PROGRESO_BOT:"):
                try:
                    return int(m.text.split(":")[1].strip())
                except:
                    continue
    except Exception as e:
        logging.warning(f"No se pudo cargar progreso: {e}")
    return 0

async def guardar_progreso(client, last_id):
    try:
        async for m in client.iter_messages('me', limit=20):
            if m.text and m.text.startswith("PROGRESO_BOT:"):
                await m.delete()
        await client.send_message('me', f"PROGRESO_BOT:{last_id}")
    except Exception as e:
        logging.error(f"Error al guardar progreso: {e}")

async def copiar_contenido(client, destino, mensaje):
    while True:
        try:
            if mensaje.media:
                await client.send_file(destino, mensaje.media, caption=mensaje.text, reply_to=TOPIC_ID)
            else:
                if mensaje.text:
                    await client.send_message(destino, mensaje.text, reply_to=TOPIC_ID)
            return True
        except FloodWaitError as e:
            logging.warning(f"FloodWait: Esperando {e.seconds}s")
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            logging.error(f"Error al copiar ID {mensaje.id}: {e}")
            await asyncio.sleep(5)
            return False

async def copiar_album(client, destino, lista_album):
    logging.info(f"Copiando album de {len(lista_album)} archivos.")
    try:
        album_caption = lista_album[0].text if lista_album[0].text else None
        for i in range(0, len(lista_album), 10):
            chunk = lista
