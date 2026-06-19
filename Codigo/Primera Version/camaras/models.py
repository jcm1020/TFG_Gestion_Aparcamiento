from django.db import models
from config.base_models import ModeloBase #Añadido para importar base_models.py

# Create your models here.
class Camara(ModeloBase):
    """
    Modelo para los dispositivos de percepcion del parking.
    Gestion de camaras (F2).
    """
    
    ESTADO_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    ip = models.GenericIPAddressField(
        unique=True,
        verbose_name='Direccion IP'
    )
    
    puerto = models.IntegerField(
        verbose_name='Puerto',
        help_text='Puerto de conexion (1-65535)'
    )
    
    usuario = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Usuario de conexion'
    )
    
    password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Password de conexion',
        help_text='Contrasena encriptada'
    )
    
    ubicacion_fisica = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Ubicacion fisica',
        help_text='Ubicacion fisica en el parking'
    )
    
    zona_aparcamiento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Zona de aparcamiento',
        help_text='Zona o area del parking'
    )
    
    resolucion = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Resolucion',
        help_text='Resolucion de captura (ej: 1920x1080)'
    )
    
    url_stream_isapi = models.CharField(
        max_length=500,
        blank=True,
        default='http://{ip}/ISAPI/Streaming/channels/101/picture',
        verbose_name='URL Stream ISAPI',
        help_text='URL de captura ISAPI. Ejemplo: http://{ip}/ISAPI/Streaming/channels/101/picture'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='offline',
        verbose_name='Estado',
        help_text='Estado de conexion de la camara'
    )
    
    capturando = models.BooleanField(
        default=False,
        verbose_name='Capturando',
        help_text='Indica si la camara esta capturando imagenes continuamente'
    )
    
    class Meta:
        verbose_name = 'Camara'
        verbose_name_plural = 'Camaras'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.ip})"
