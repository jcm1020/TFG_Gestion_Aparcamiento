from django.db import models
from config.base_models import ModeloBase #Añadio para importar base_models.py
from camaras.models import Camara  #Añadido para importar de Camara

# Create your models here.
class Imagen(ModeloBase):
    """
    Modelo para las imagenes capturadas por las camaras del sistema.
    Gestion de imagenes (F3).
    """
    
    NIVEL_PRIVACIDAD_CHOICES = [
        ('publico', 'Publico'),
        ('privado', 'Privado'),
        ('confidencial', 'Confidencial'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesada', 'Procesada'),
    ]
    
    nombre = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre'
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora de captura'
    )
    
    ruta_archivo = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ruta del archivo',
        help_text='Ruta del archivo de imagen'
    )
    
    tamano = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Tamano (bytes)'
    )
    
    camara = models.ForeignKey(
        Camara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='imagenes',
        verbose_name='Camara',
        help_text='Camara que capturo la imagen'
    )
    
    nivel_privacidad = models.CharField(
        max_length=20,
        choices=NIVEL_PRIVACIDAD_CHOICES,
        default='privado',
        verbose_name='Nivel de privacidad'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
        help_text='Estado de procesamiento'
    )
    
    comentarios = models.TextField(
        blank=True,
        verbose_name='Comentarios'
    )
    
    es_referencia = models.BooleanField(
        default=False,
        verbose_name='Imagen de referencia',
        help_text='Imagen usada para inicializar el sistema y crear objetos de referencia'
    )
    
    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imagenes'
        ordering = ['-timestamp']
    
    def __str__(self):
        return self.nombre or f"Imagen {self.id}"