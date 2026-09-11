from django.db import models
from config.base_models import ModeloBase, Activo  #Añadido para importar base_models

# Create your models here.


class Usuarios(ModeloBase, Activo):
    """
    Modelo para los administradores del nucleo de gestion del sistema.
    Gestion de usuarios del sistema.
    """
    
    '''
    Herencia múltiple:
    - ModeloBase: Proporciona fecha_creacion y fecha_actualizacion automáticos
    - Activo: Aporta el campo activo para estado lógico de registros
    
    Responsable de gestionar:
    - Autenticación de usuarios (login/password encriptado)
    - Control de acceso por niveles (Básico vs Administrador)
    - Información personal completa (nombre, email, teléfono, dirección)
    - Relación con cliente/propietario a través de id_usuario
    
    Uso recomendado:
    from apps.usuarios.models import Usuarios
    usuario = Usuarios.objects.get(login='admin')
    print(f"{usuario.nombre} es {get_level_name(usuario.nivel_acceso)}")
    '''
    
    # CONSTANTES DE CONFIGURACION
    """
    Diccionario de opciones para el campo nivel_acceso.
    
    Nivel 1 (Basico):
    - Puede leer información de espacios y usuarios
    - No puede crear, editar o eliminar registros
    
    Nivel 2 (Administrador):
    - Tiene permisos completos para gestionar todo el sistema
    - Puede crear nuevos usuarios, espacios, modificar configuraciones
    """
    NIVEL_ACCESO = [
        (1, 'Basico'),
        (2, 'Administrador'),
    ]
    
    # CAMPOS DEL MODELO
    id_usuario = models.IntegerField(
        null=True, # Permite valores NULL (nulo) en la base de datos
        blank=True, # El formulario puede dejarlo vacío y no mostrar error
        verbose_name='ID Usuario', # Nombre que aparecerá en Django Admin y formularios
        help_text='Identificador del cliente o propietario' # Ayuda para administradores
    )
    
    nombre = models.CharField(max_length=100, verbose_name='Nombre') # Longitud máxima permitida: 100 caracteres (ej: "Juan")

    apellidos = models.CharField(max_length=150, blank=True, verbose_name='Apellidos')
    
    # Único en toda la base de datos para evitar duplicados por email
    email = models.EmailField(unique=True, verbose_name='Correo electronico')    
    
    # Longitud máxima 20 caracteres (permite código país +34 y espacios)
    # Opcional - no es obligatorio registrarlo
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Telefono')
    
    # Longitud considerable para direcciones largas
    # Opcional - no es obligatorio
    direccion = models.CharField(max_length=255, blank=True, verbose_name='Direccion')
    
    # Longitud máxima: 50 caracteres (ej: "jua", "admin")
    # Único en la base de datos - es el identificador para login
    login = models.CharField(max_length=50, unique=True, verbose_name='Usuario de login')
    
    
    """
    Contraseña del usuario, ALMACENADA COMO HASH (no texto plano).
    
    🔒 SEGURIDAD IMPORTANTE:
    - Django usa por defecto 'make_password()' que aplica PBKDF2-SHA256
    - Nunca se almacena la contraseña en texto legible
    - Al crear/editar, usar make_password() desde views.py
    
    Ejemplo de creación segura:
    >>> from django.contrib.auth.hashers import make_password
    >>> password_hash = make_password('mi_contra_segura123')
    >>> user.password = password_hash
    >>> user.save()
    
    Verificación de contraseña:
    >>> from django.contrib.auth.hashers import check_password
    >>> check_password('mi_contra_segura123', password_hash)  # Retorna True/False
    
    Longitud de 255 caracteres cubre:
    - PBKDF2-SHA256 (más rápido, recomendado para apps web simples)
    - Argon2 y bcrypt (más lento, pero más seguros para apps críticas)
    
    Nunca mostrar password en logs o errores.
    """
    password = models.CharField(
        max_length=255, # Longitud suficiente para hash SHA-256 (ej: argon2 o PBKDF2)
        verbose_name='Password', # Nombre en interfaz Django Admin
        help_text='Contraseña encriptada'  
    )
    
    
    """
    Permisos y privilegios del usuario.
    
    Valores permitidos:
    - 1 (Básico): Solo lectura, no puede crear/editar/eliminar nada
    - 2 (Administrador): CRUD completo sobre usuarios y espacios
    """
    nivel_acceso = models.IntegerField(
        choices=NIVEL_ACCESO,
        default=1,
        verbose_name='Nivel de acceso',
        help_text='1-Basico, 2-Administrador'
    )
    
    # Campo de texto libre para notas adicionales.
    comentarios = models.TextField(
        blank=True,
        verbose_name='Comentarios',
        help_text='Observaciones adicionales'
    )
    
    
    # ==============================================================================
    # METACLASES Y CONFIGURACIÓN DE LA BASE DE DATOS
    # ==============================================================================
        
    class Meta:
        verbose_name = 'Usuario del Nucleo'
        verbose_name_plural = 'Usuarios del Nucleo'
        ordering = ['-fecha_creacion']


    # ==============================================================================
    # MÉTODOS PERSONALIZADOS
    # ==============================================================================
        
    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.login})"
        """
        Método especial que define la representación string del objeto.
        
        Usos:
        1. En admin Django: muestra esta cadena en lugar de "<Usuarios object at 0x...>"
        2. En logs y debuggers: útil para debugging rápido
        3. En queries de consola Python: representa el usuario legible
        
        Formato: "{nombre} {apellidos} (login)"
        
        Ejemplos de salida:
        - "Juan Pérez (jua)"          # Nombre completo con login entre paréntesis
        - "María González (maria123)"  
        - "Carlos (cari)"              # Si apellidos está vacío
        
        Por qué este formato:
        - Identificación rápida sin mostrar datos sensibles como password/email
        - El login entre paréntesis es un identificador único reconocible
        """