from django.db import models

from apps.espacios.models import Espacio
from config.base_models import ModeloBase, Activo

# Create your models here.

PLANTILLA_ISAPI = 'http://{ip}/ISAPI/Streaming/channels/101/picture'


class Camara(ModeloBase, Activo):
    ESTADO_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    espacio_fisico = models.ForeignKey(
        Espacio,
        on_delete=models.PROTECT,
        related_name='camaras',
        verbose_name='Espacio',
        help_text='Espacio fisico al que pertenece la camara',
    )

    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
    )

    ip = models.GenericIPAddressField(
        unique=True,
        verbose_name='Direccion IP',
    )

    puerto = models.IntegerField(
        verbose_name='Puerto',
        help_text='Puerto de conexion (1-65535)',
    )

    usuario = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Usuario de conexion',
        help_text='Usuario para la autenticacion HTTP Digest de la camara',
    )

    password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Password de conexion',
        help_text='Se guarda sin cifrar porque la camara exige HTTP Digest, '
 'que necesita el valor original. No es una cuenta de usuario.',
    )

    resolucion = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Resolucion',
        help_text='Resolucion de captura (ej: 1920x1080)',
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='offline',
        verbose_name='Estado',
        help_text='Estado de conexion de la camara',
    )

    url_stream_isapi = models.CharField(
        max_length=500,
        default=PLANTILLA_ISAPI,
        verbose_name='URL de captura ISAPI',
        help_text='Plantilla de captura. Usa {ip} como marcador.',
    )

    class Meta:
        verbose_name = 'Camara'
        verbose_name_plural = 'Camaras'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.ip})'


class ControlSistema(models.Model):
    """
    Un registro por cada proceso de deteccion en ejecucion.

    La clave es el pid real del proceso, de modo que la vivacidad se puede
    comprobar contra el sistema operativo y no solo contra la base de datos:
    si el servidor se cae, quedan filas con en_ejecucion=True que ya no
    corresponden a nada y se reconcilian al arrancar.
    """

    camara = models.ForeignKey(
        Camara,
        on_delete=models.CASCADE,
        related_name='procesos',
        verbose_name='Camara',
        help_text='Camara a la que pertenece este proceso',
    )

    pid = models.PositiveIntegerField(
        primary_key=True,
        verbose_name='PID',
        help_text='Identificador del proceso en el sistema operativo',
    )

    en_ejecucion = models.BooleanField(
        default=True,
        verbose_name='En ejecucion',
    )

    inicio = models.DateTimeField(
        verbose_name='Inicio del proceso',
    )

    class Meta:
        verbose_name = 'Control del sistema'
        verbose_name_plural = 'Controles del sistema'
        ordering = ['-inicio']

    def __str__(self):
        return f'{self.camara.nombre} (pid {self.pid})'
