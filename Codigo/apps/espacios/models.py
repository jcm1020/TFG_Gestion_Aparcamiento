from django.db import models
from config.base_models import ModeloBase  #Añadido para importar base_models

# Create your models here.


class Espacio(ModeloBase):
    nombre = models.CharField(
        max_length=100,  # Longitud máxima permitida: 100 caracteres (ej: "Aparcamiento 1 UBU")
        unique=True, # El formulario puede dejarlo vacío y no mostrar error
        verbose_name='Nombre', # Nombre que aparecerá en Django Admin y formularios
        help_text='Identificador de espacio', # Ayuda para administradores
    )

    ubicacion = models.CharField(
        max_length=100,
        blank=True, # El formulario puede dejarlo vacío y no mostrar error
        verbose_name='Ubicación', # Nombre que aparecerá en Django Admin y formularios
    )
    
    descripcion = models.TextField(
        blank=True, # El formulario puede dejarlo vacío y no mostrar error
        verbose_name='Descripción', # Nombre que aparecerá en Django Admin y formularios
    )

    class Meta:
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios' 
        ordering = ['nombre']

    def __str__(self):
        if self.ubicacion:
            if self.descripcion:
                return f'{self.nombre} ({self.ubicacion}, {self.descripcion})'
            return f'{self.nombre} ({self.ubicacion})'            
        return self.nombre


class Localizacion(ModeloBase):
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre',
    )

    descripcion = models.TextField(
        blank=True, # El formulario puede dejarlo vacío y no mostrar error
        verbose_name='Descripción', # Nombre que aparecerá en Django Admin y formularios
    )

    class Meta:
        verbose_name = 'Localización'
        verbose_name_plural = 'Localizaciones'

    def __str__(self):
        if self.descripcion:
            return f'{self.nombre} ({self.descripcion})' 
        return self.nombre
