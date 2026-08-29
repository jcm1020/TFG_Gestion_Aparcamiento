"""
Forms para la app Usuarios (F1)
"""
from django import forms
from .models import Usuarios


class UsuariosForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del nucleo."""

    
