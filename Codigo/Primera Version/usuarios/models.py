from django.db import models
from config.base_models import ModeloBase, Activo  #Añadido por mi para importar base_models

# Create your models here.

class UsuarioNucleo(ModeloBase, Activo):
    """
    Modelo para los administradores del nucleo de gestion del sistema.
    Gestion de usuarios del nucleo (F1).
    """
    
    NIVEL_ACCESO_CHOICES = [
        (1, 'Basico'),
        (2, 'Administrador'),
    ]
    
    id_cliente = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID Cliente',
        help_text='Identificador del cliente o propietario'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )
    
    apellidos = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Apellidos'
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name='Correo electronico'
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefono'
    )
    
    direccion = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Direccion'
    )
    
    login = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Usuario de login'
    )
    
    password = models.CharField(
        max_length=255,
        verbose_name='Password',
        help_text='Contraseña encriptada'
    )
    
    nivel_acceso = models.IntegerField(
        choices=NIVEL_ACCESO_CHOICES,
        default=1,
        verbose_name='Nivel de acceso',
        help_text='1-Basico, 2-Administrador'
    )
    
    comentarios = models.TextField(
        blank=True,
        verbose_name='Comentarios',
        help_text='Observaciones adicionales'
    )
    
    class Meta:
        verbose_name = 'Usuario del Nucleo'
        verbose_name_plural = 'Usuarios del Nucleo'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.login})"
