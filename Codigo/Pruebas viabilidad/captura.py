import requests
import re
import time
from datetime import datetime
from io import BytesIO
from PIL import Image
import os

# URL de la cámara que proporciona un flujo MJPEG (Motion JPEG)
# MJPEG es un formato de video donde cada frame es una imagen JPEG completa
MJPEG_URL = "http://x.x.x.x/mjpg/video.mjpg"
# Nombre del directorio donde se guardarán las imágenes capturadas
DIRECTORIO = "Camara"

def crear_directorio():
    """
    Función que crea el directorio para almacenar las imágenes si no existe.
    
    Esta función verifica si el directorio especificado en la variable DIRECTORIO
    ya existe en el sistema de archivos. Si no existe, lo crea y muestra un mensaje
    confirmando su creación. Si ya existe, simplemente muestra un mensaje indicando
    que se usará el directorio existente.
    """
    # os.path.exists() comprueba si la ruta especificada existe en el sistema de archivos
    if not os.path.exists(DIRECTORIO):
        # os.makedirs() crea el directorio (y todos los directorios padres necesarios)
        os.makedirs(DIRECTORIO)
        print(f"✓ Directorio '{DIRECTORIO}' creado")
    else:
        print(f"✓ Usando directorio existente '{DIRECTORIO}'")

def extraer_frame_mjpeg():
    """
    Función que se conecta a la URL MJPEG, extrae un frame individual y lo guarda como archivo.
    
    Esta función realiza una petición HTTP a la URL MJPEG especificada y procesa el flujo
    de datos para extraer un frame completo (una imagen JPEG) del flujo continuo.
    El frame se guarda en el directorio especificado con un nombre basado en la fecha y hora actual.
    
    Returns:
        bool: True si se extrajo y guardó correctamente un frame, False en caso contrario.
    """
    # Cabeceras HTTP para simular un navegador web y evitar posibles bloqueos
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    
    try:
        # Realizamos una petición GET a la URL MJPEG con streaming activado
        # stream=True permite procesar la respuesta en fragmentos sin cargar todo en memoria
        # timeout=15 establece un tiempo máximo de espera de 15 segundos
        resp = requests.get(MJPEG_URL, headers=headers, stream=True, timeout=15)
        # raise_for_status() lanza una excepción si la respuesta HTTP indica un error (códigos 4xx o 5xx)
        resp.raise_for_status()
        
        # Buffer para almacenar los datos recibidos del flujo MJPEG
        buffer = b""
        # Marcadores que indican el inicio y fin de una imagen JPEG
        jpg_start = b"\xff\xd8"  # SOI (Start of Image) - marcador de inicio JPG
        jpg_end = b"\xff\xd9"    # EOI (End of Image) - marcador de fin JPG
        
        # Iteramos sobre los fragmentos de datos recibidos del servidor
        # chunk_size=1024 especifica que leemos en fragmentos de 1024 bytes
        for chunk in resp.iter_content(chunk_size=1024):
            # Si el fragmento contiene datos, lo añadimos al buffer
            if chunk:
                buffer += chunk
                
                # Posición inicial para buscar el siguiente frame en el buffer
                start_pos = 0
                # Bucle infinito para buscar todos los frames posibles en el buffer actual
                while True:
                    # Buscamos el marcador de inicio de una imagen JPEG en el buffer
                    start_idx = buffer.find(jpg_start, start_pos)
                    # Si no encontramos el marcador de inicio, salimos del bucle
                    if start_idx == -1:
                        break
                    
                    # Buscamos el marcador de fin de la imagen JPEG a partir del inicio encontrado
                    end_idx = buffer.find(jpg_end, start_idx + 2)
                    # Si encontramos ambos marcadores, tenemos una imagen completa
                    if end_idx != -1:
                        # Extraemos los datos de la imagen JPEG completa
                        jpg_data = buffer[start_idx:end_idx + 2]
                        
                        # Generamos un nombre de archivo único basado en la fecha y hora actual
                        # strftime() formatea la fecha y hora según el patrón especificado
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        # os.path.join() une el directorio con el nombre de archivo usando el separador correcto
                        filename = os.path.join(DIRECTORIO, f"frame_{ts}.jpg")
                        
                        # Abrimos el archivo en modo binario de escritura y guardamos los datos de la imagen
                        with open(filename, "wb") as f:
                            f.write(jpg_data)
                        
                        # Mostramos un mensaje confirmando que se ha guardado la imagen
                        print(f"✓ Guardada: {filename} ({len(jpg_data)} bytes)")
                        
                        # Eliminamos el frame procesado del buffer para liberar memoria
                        buffer = buffer[end_idx + 2:]
                        # Devolvemos True para indicar que hemos procesado correctamente un frame
                        return True  # Salimos después de guardar un frame
                    # Si no encontramos el marcador de fin, continuamos buscando desde la siguiente posición
                    start_pos = start_idx + 1
        # Si salimos del bucle sin encontrar un frame completo, devolvemos False
        return False
        
    except Exception as e:
        # Capturamos cualquier excepción que ocurra durante el proceso y mostramos un mensaje de error
        print(f"Error: {e}")
        return False

# Creamos el directorio al inicio del programa para asegurar que exista
crear_directorio()

# Bucle principal del programa
print("Capturando frames cada 10 segundos...")
print("Presiona Ctrl+C para parar")
# Bucle infinito que se ejecuta hasta que el usuario lo interrumpe con Ctrl+C
while True:
    # Llamamos a la función para extraer y guardar un frame
    extraer_frame_mjpeg()
    # Esperamos 10 segundos antes de capturar el siguiente frame
    time.sleep(10)
