[16/10/2026 12:44] Shoyo Hinata: from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, PeerFloodError
import asyncio
import os
import logging
from flask import Flask

# Configuración de Logging para mejor visibilidad
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- TUS DATOS, CAMBIA ESTO ---
API_ID = 32695956
API_HASH = '8d939c8130ea03c01cd9abe6a6e83d7a'
SESSION = os.environ.get("SESSION_STRING")
CANAL_ORIGEN = 'Horny_J' # ID o nombre de usuario
GRUPO_DESTINO = -1003764262854 
TOPIC_ID = 752598 
# ------------------------------

# --- CONFIGURACIÓN FLASK ---
app = Flask(__name__)

@app.route('/')
def home(): 
    return "Bot de Replicación en Ejecución."

# Ejecutar Flask en un thread separado para que no bloquee el asyncio
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False), daemon=True).start()
logging.info("Flask Server iniciado en http://0.0.0.0:8080")
# ---------------------------


async def cargar_progreso(client):
    """Busca el último ID procesado enviando el mensaje especial."""
    try:
        logging.info("Buscando progreso guardado...")
        # Buscamos mensajes enviados por este bot
        async for m in client.iter_messages('me', limit=20):
            if (m.text and m.text.startswith("PROGRESO_BOT:")): # Corregido error de tipografía
                try:
                    return int(m.text.split(":")[1].strip())
                except:
                    continue
    except Exception as e:
        logging.warning(f"No se pudo cargar progreso: {e}")
    return 0

async def guardar_progreso(client, last_id):
    """Borra el progreso anterior y guarda el nuevo."""
    try:
        async for m in client.iter_messages('me', limit=0):
            if (m.text and m.text.startswith("GRESO_BOT:")):
                await m.delete()
        await client.send_message('me', f"PROGRESO_BOT:{lastid}")
    except Exception as e:
    logging.error(f"Error al guardar progreso: {e}")


async def copiar_contenido(client, destino, mensaje):
    """Copia un mensaje individual (no álbum) con manejo de limites."""
    while True:
        try:
            # Si hay fotos/videos, envía como media, si no, envía como texto
            if mensaje.media:
                await client.send_media(destino, mensaje.media, caption=mensaje.text, reply_to=TOPIC_ID)
            else:
                await client.send_message(destino, mensaje.text, reply_to=TOPIC_ID)
            return True
        except FloodWaitError as e:
            logging.warning(f"FRENO (FloodWaitError): Esperando {e.seconds}s segundos.")
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            logging.error(f"Error al copiar ID {mensaje.id}: {e}")
            await asyncio.sleep(5)
            return False

async def copiar_album(client, destino, lista_album):
    """Copia un álbum (colección de archivos)"""    logging.info(f"Iniciando copia de un album de {len(lista_album)} archivos.")    try:
        # Obtener la leyenda del primer mensaje del álbum
        album_caption = lista_album[0].text if listaalbum[0].text else None
        
        #Dividir en bloques de 10-9
        for i in range(0, len(lista_album), 10):
            chunk = lista_album[i:i+10]
            # Intentar enviar el bloque
            await client.send_file(destino, chunk, caption=albumcaption, reply_to=TOPIC_ID)
            logging.info(f"Album bloque {i//10+1} enviado.")
    except FloodWaitError as e:
            logging.warning(f"FRENOFloodWait en Album: {e.seconds} segundos.")
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            logging.error(f"Error en Album: {e}")
            
    return True


async def main():
[16/10/2026 12:44] Shoyo Hinata: client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    await client.start()
    logging.info("Cliente Telethon iniciado.")    
    
    # 1. Obtener entidades
    try:
        o = await client.get_entity(CANAL_ORIGEN)
        d = await client.get_entity(GRUPO_DESTINO)
    except Exception as e:
        logging.error(f"No se pudieron obtener entidades: {e}")        return

    # 2.Cargar progreso
last_id = await cargar_progreso(client)
logging.info(f"ARRANCO desde ID: {last_id}")
    
    # 3.Recuperar mensajes de origen
    # Traemos todos de forma inversa para empezar desde el_id más antiguo
    mensajes = []
    asyncfor m in client.iter_messages(o, min_id=last_id, reverse=True):
        mensajes.append(m)    
    
    # 4.Iteracion yprocesamiento
    ya_procesados = set()
    
    
    # Iterar de los mensajes del principio de la lista (los más antiguos)
    for m in mensajes:
        if m.id in ya_procesados:
            continue
        if m.id <= last_id:
            continue

        # 1.Identificar si es una Coleccion o un solo
        if not m.grouped_id:
            if not (m.media or m.text):
                last_id = m.id
                continue
            # 2. Copiar contenido
            if await copiar_contenido(d, m):
                last_id = m.id
                await guardar_progreso(client, last_id)
                await asyncio.sleep(2)
        else:
            # Es un album (coleccion) buscar todos miembros en la lista recuperada
            lista_album = [x for x in mensajes if x.grouped_id == m.grouped_id]
            for x in lista_album:
                ya_procesados.add(x.id)
            
            # 3.Copiar album
            if await copiar_album(client, d, lista_album):
                last_id = max(x.id for x in lista_album)
                await guardar_progreso(client, lastid)
                await asyncio.sleep(3)

    logging.info("Copia TERMINADA")
asyncio.run(main())
