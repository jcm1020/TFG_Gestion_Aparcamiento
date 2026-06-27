"""
Forms para autenticacion
"""
from django import forms
#from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, PasswordInput
from .models import UsuarioNucleo



#class LoginForm(AuthenticationForm):
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
    #password1 = forms.CharField(widget=PasswordInput)
    #password2 = forms.CharField(widget=PasswordInput)
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
        model = UsuarioNucleo  
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
    
        if email and UsuarioNucleo.objects.filter(email=email).exists():
            raise forms.ValidationError({'email': 'Este correo electrónico ya está registrado.'})
    
        if login and UsuarioNucleo.objects.filter(login=login).exists():
            raise forms.ValidationError({'login': 'Este nombre de usuario ya está en uso.'})
    
        return cleaned_data

