"""
Modelos base para todas las apps
"""
from django.db import models
from django.utils import timezone

class ModeloBase(models.Model):
    """Modelo base con campos comunes"""
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        abstract = True
        
class Activo(models.Model):
    """Mixin para modelos con campo activo"""
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        abstract = True