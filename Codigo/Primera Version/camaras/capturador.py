import threading
import time
import logging
import os
from datetime import datetime
import requests
from requests.auth import HTTPDigestAuth
from django.db import close_old_connections
from .models import Camara
from imagenes.models import Imagen

logger = logging.getLogger(__name__)

DIRECTORIO_CAMARA = "Camara"

hilos = {}
hilos_lock = threading.Lock()


def _ruta_camara():
    if not os.path.exists(DIRECTORIO_CAMARA):
        os.makedirs(DIRECTORIO_CAMARA)
    return DIRECTORIO_CAMARA


PLANTILLA_ISAPI_DEFAULT = 'http://{ip}/ISAPI/Streaming/channels/101/picture'


def capturar_camara(camara):
    try:
        plantilla = camara.url_stream_isapi
        if not plantilla or '{ip}' not in plantilla:
            plantilla = PLANTILLA_ISAPI_DEFAULT
        url = plantilla.format(ip=camara.ip)
        response = requests.get(
            url,
            auth=HTTPDigestAuth(camara.usuario, camara.password),
            timeout=10
        )
        if response.status_code != 200:
            logger.warning("Error capturando %s: HTTP %s", camara.nombre, response.status_code)
            return False

        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"camara_{camara.id}_{ts}.jpg"
        ruta = os.path.join(_ruta_camara(), filename)

        with open(ruta, "wb") as f:
            f.write(response.content)

        Imagen.objects.create(
            nombre=f"Captura {camara.nombre} {ts}",
            ruta_archivo=ruta,
            tamano=len(response.content),
            camara=camara,
            nivel_privacidad='privado',
            estado='pendiente'
        )

        logger.info("Captura guardada: %s (%d bytes)", filename, len(response.content))
        return True

    except requests.exceptions.RequestException as e:
        logger.error("Error de conexion al capturar %s: %s", camara.nombre, e)
        return False
    except Exception as e:
        logger.error("Error inesperado capturando %s: %s", camara.nombre, e)
        return False


def hilo_captura_continua(camara_id):
    close_old_connections()
    logger.info("Hilo de captura continua iniciado para camara %d", camara_id)

    try:
        while True:
            close_old_connections()
            try:
                camara = Camara.objects.get(pk=camara_id)
            except Camara.DoesNotExist:
                logger.warning("Camara %d eliminada, deteniendo captura", camara_id)
                break

            if not camara.capturando:
                logger.info("Captura detenida para camara %d", camara_id)
                break

            capturar_camara(camara)

            for _ in range(50):
                time.sleep(0.1)
                try:
                    camara = Camara.objects.get(pk=camara_id)
                    if not camara.capturando:
                        logger.info("Captura detenida durante espera para camara %d", camara_id)
                        return
                except Camara.DoesNotExist:
                    return

    except Exception as e:
        logger.error("Error en hilo de captura %d: %s", camara_id, e)
    finally:
        Camara.objects.filter(pk=camara_id).update(capturando=False)
        with hilos_lock:
            hilos.pop(camara_id, None)
        close_old_connections()
        logger.info("Hilo de captura finalizado para camara %d", camara_id)


def iniciar_captura(camara_id):
    with hilos_lock:
        if camara_id in hilos and hilos[camara_id].is_alive():
            logger.warning("Ya hay una captura activa para camara %d", camara_id)
            return False

        Camara.objects.filter(pk=camara_id).update(capturando=True)

        hilo = threading.Thread(
            target=hilo_captura_continua,
            args=(camara_id,),
            name=f"Captura-{camara_id}",
            daemon=True
        )
        hilo.start()
        hilos[camara_id] = hilo
        logger.info("Captura iniciada para camara %d", camara_id)
        return True


def detener_captura(camara_id):
    Camara.objects.filter(pk=camara_id).update(capturando=False)
    with hilos_lock:
        hilos.pop(camara_id, None)
    logger.info("Senial de detencion enviada para camara %d", camara_id)
    return True


def esta_capturando(camara_id):
    with hilos_lock:
        hilo = hilos.get(camara_id)
        if hilo and hilo.is_alive():
            return True
        if hilo:
            hilos.pop(camara_id, None)
        return False
