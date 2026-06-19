"""
Forms para la app Usuarios (F1)
"""
from django import forms
from .models import UsuarioNucleo


class UsuarioNucleoForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del nucleo."""
    
    '''password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena'}),
        required=False,
        help_text='Dejar en blanco para mantener la actual.'
    )'''
    nueva_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}),
        required=False,
        help_text='Dejar en blanco para mantener la actual.'
    )
    
    class Meta:
        model = UsuarioNucleo
        fields = [
            'nombre', 'apellidos', 'email', 'telefono', 'direccion',
            'login', 'nueva_password', 'nivel_acceso', 'comentarios', 'activo'
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
    
    '''
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password and not self.instance.pk:
            raise forms.ValidationError('La contrasena es obligatoria para nuevos usuarios.')
        return password
    '''
        
    def clean_nueva_password(self):
        password = self.cleaned_data.get('nueva_password')
        if not password and not self.instance.pk:
            raise forms.ValidationError('La contraseña es obligatoria.')
        return password
