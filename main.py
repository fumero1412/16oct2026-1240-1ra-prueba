from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
import asyncio
import os
import logging
import threading
from flask import Flask

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- DATOS DESDE VARIABLES DE ENTORNO, NUNCA EN EL CODIGO ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION = os.environ.get("SESSION_STRING")
CANAL_ORIGEN = os.environ.get("CANAL_ORIGEN", "Horny_J")
GRUPO_DESTINO = int(os.environ.get("GRUPO_DESTINO", "-1003764262854"))
TOPIC_ID = int(os.environ.get("TOPIC_ID", "752598"))
# ------------------------------------------------------------

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
            chunk = lista_album[i:i+10]
            files = [x.media for x in chunk if x.media]
            if files:
                await client.send_file(destino, files, caption=album_caption if i==0 else None, reply_to=TOPIC_ID)
                logging.info(f"Album bloque {i//10+1} enviado.")
    except FloodWaitError as e:
        logging.warning(f"FloodWait en Album: {e.seconds}s")
        await asyncio.sleep(e.seconds + 5)
    except Exception as e:
        logging.error(f"Error en Album: {e}")
    return True

async def main():
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    await client.start()
    logging.info("Cliente Telethon iniciado.")

    try:
        o = await client.get_entity(CANAL_ORIGEN)
        d = await client.get_entity(GRUPO_DESTINO)
    except Exception as e:
        logging.error(f"No se pudieron obtener entidades: {e}")
        return

    last_id = await cargar_progreso(client)
    logging.info(f"ARRANCO DESDE: {last_id}")

    mensajes = []
    async for m in client.iter_messages(o, min_id=last_id, reverse=True):
        mensajes.append(m)

    ya_procesados = set()

for m in mensajes:
        if m.id in ya_procesados or m.id <= last_id:
            continue

        if not m.grouped_id:
            if not (m.media or m.text):
                last_id = m.id
                continue
            if await copiar_contenido(client, d, m):
                last_id = m.id
                await guardar_progreso(client, last_id)
                await asyncio.sleep(2)
        else:
            lista_album = [x for x in mensajes if x.grouped_id == m.grouped_id]
            for x in lista_album:
                ya_procesados.add(x.id)
            if await copiar_album(client, d, lista_album):
                last_id = max(x.id for x in lista_album)
                await guardar_progreso(client, last_id)
                await asyncio.sleep(3)
    logging.info("Copia TERMINADA")

asyncio.run(main())
