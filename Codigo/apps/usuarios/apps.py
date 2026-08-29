from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    # Mejorar la organización y permitir referencias como {% url 'usuarios:lista' %} en lugar de {% url 'usuarios_lista' %}.
    label = 'usuarios'  # Añadido para permitir usar namespace en templates
