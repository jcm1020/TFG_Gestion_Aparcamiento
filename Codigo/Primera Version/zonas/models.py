"""
Modelos para la app Zonas (F4 - Gestion de Zonas del Parking)
"""
from django.db import models
from config.base_models import ModeloBase, Activo
from camaras.models import Camara

# Create your models here.

class Zona(ModeloBase, Activo):
    """
    Modelo para las zonas del parking.
    Definidas mediante ficheros DXF (plazas, entradas, salidas, areas).
    Gestion de zonas (F4).
    """
    
    TIPO_CHOICES = [
        ('plaza', 'Plaza'),
        ('calzada', 'Calzada'),
        ('acera', 'Acera'),
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('area', 'Area'),
        ('restringida', 'Restringida'),
        ('otro', 'Otro'),
    ]
    
    UNIDAD_MEDIDA_CHOICES = [
        ('metros', 'Metros'),
        ('centimetros', 'Centimetros'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    tipo = models.CharField(
        max_length=50,
        verbose_name='Tipo'
    )
    
    tag = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tag',
        help_text='Etiqueta manual para la zona'
    )
    
    coordenadas_posicion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Coordenadas de posicion',
        help_text='Coordenadas X, Y de posicion'
    )
    
    ancho = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ancho (metros)'
    )
    
    largo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Largo (metros)'
    )
    
    rotacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Rotacion (grados)',
        help_text='Angulo de rotacion (0-360 grados)'
    )
    
    centroide = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Centroide',
        help_text='Coordenadas del centroide (Xc, Yc)'
    )
    
    camara_asignada = models.ForeignKey(
        Camara,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zonas',
        verbose_name='Camara asignada',
        help_text='Camara asignada para supervisar'
    )
    
    vertices = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Vertices del poligono',
        help_text='Coordenadas del poligono de la zona'
    )
    
    dxf_origen = models.ForeignKey(
        'FicherosDXF',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zonas',
        verbose_name='DXF de origen'
    )
    
    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class FicherosDXF(models.Model):
    """
    Modelo para gestionar los archivos DXF subidos.
    Solo un DXF puede estar activo a la vez.
    """
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesado', 'Procesado'),
    ]
    
    UNIDAD_MEDIDA_CHOICES = [
        ('metros', 'Metros'),
        ('centimetros', 'Centimetros'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    archivo = models.FileField(
        upload_to='dxf/',
        verbose_name='Archivo DXF',
        help_text='Fichero DXF del parking'
    )
    
    escala = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Escala',
        help_text='Escala del plano DXF (ej: 1:100)'
    )
    
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_MEDIDA_CHOICES,
        default='metros',
        verbose_name='Unidad de medida'
    )
    
    activo = models.BooleanField(
        default=False,
        verbose_name='Activo',
        help_text='Solo un DXF puede estar activo'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
        help_text='Estado del procesamiento del DXF'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creacion'
    )
    
    class Meta:
        verbose_name = 'Fichero DXF'
        verbose_name_plural = 'Ficheros DXF'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"
    
    def save(self, *args, **kwargs):
        if self.activo:
            FicherosDXF.objects.filter(activo=True).exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)
