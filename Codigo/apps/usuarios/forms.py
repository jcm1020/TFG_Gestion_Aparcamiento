"""
Forms para la app Usuarios (F1)
"""
from django import forms
from .models import Usuarios


class UsuariosForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del nucleo."""



    class Meta:
        model = Usuarios
        fields = [
            'nombre', 'apellidos', 'email', 'telefono', 'direccion',
            'login', 'password', 'nivel_acceso', 'comentarios', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'placeholder': '+34 600 000 000'}),
            'direccion': forms.TextInput(attrs={'placeholder': 'Direccion'}),
            'login': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
            'comentarios': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentarios adicionales'}),
        }


