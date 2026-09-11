"""
Forms para la app Usuarios
"""
from django import forms
from .models import Usuarios
from django.forms import ModelForm, PasswordInput # Para LoginForm y RegsitroForm

class UsuariosForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del sistema."""
    
    nueva_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}),
        required=False,
        help_text='Dejar en blanco para mantener la actual.'
    )


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
        
    def clean_nueva_password(self):
        password = self.cleaned_data.get('nueva_password')
        if not password and not self.instance.pk:
            raise forms.ValidationError('La contraseña es obligatoria.')
        return password
        
        

"""
Forms para autenticacion
"""

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )
    remember = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Recordarme'
    )


class RegistroForm(ModelForm):
    password1 = forms.CharField(
        widget=PasswordInput(attrs={'placeholder': 'Contraseña'}),
        label='Contraseña'
    )

    password2 = forms.CharField(
        widget=PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        label='Confirmar contraseña'
    )

    login = forms.CharField(
        label='Usuario de login',
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
        help_text='Nombre para iniciar sesión'
    )

    class Meta:
        model = Usuarios
        fields = ['nombre', 'apellidos', 'login', 'email', 'telefono', 'password1', 'password2']

    def clean_password2(self):
        # Validar que password1 == password2
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Las contraseñas no coinciden')
        return password2

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        login = cleaned_data.get('login')

        if email and Usuarios.objects.filter(email=email).exists():
            raise forms.ValidationError({'email': 'Este correo electrónico ya está registrado.'})

        if login and Usuarios.objects.filter(login=login).exists():
            raise forms.ValidationError({'login': 'Este nombre de usuario ya está en uso.'})

        return cleaned_data
