"""
Forms para la app Usuarios
"""
from django import forms
from .models import Usuarios
from django.forms import ModelForm, PasswordInput # Para LoginForm y RegsitroForm

from django.contrib.auth.hashers import make_password

class UsuariosForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del sistema."""
    
    nueva_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}),
        required=False,
        help_text='Dejar en blanco para mantener la actual.'
    )

    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'}),
        required=False,
        help_text='Debe coincidir con la contraseña.'
    )

    class Meta:
        model = Usuarios
        # 'password' no se incluye a proposito: en ese campo solo se guarda el hash,
        # que se genera con save() a partir de nueva_password. Si se listara aqui, el
        # formulario pediria un hash que el usuario no puede teclear, problema del bug existente.
        fields = [
            'nombre', 'apellidos', 'email', 'telefono', 'direccion',
            'login', 'nivel_acceso', 'comentarios', 'activo'
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
    
    # Posibles combinaciones que se cubren con este nuevo metodo clean y save:
    # Situación	    nueva_password	    confirmar_password	Resultado
    # Alta (alta)	vacía	            da igual	        Error: «La contraseña es obligatoria.»
    # Alta	        escrita	            vacía o distinta	Error: «Las contraseñas no coinciden.»
    # Alta	        escrita	            igual	            Válido
    # Edición	    vacía	            vacía	            Válido, y no se toca el hash
    # Edición	    escrita	            vacía o distinta	Error: «Las contraseñas no coinciden.»
    # Edición	    escrita	            igual	            Válido, se genera hash nuevo    
    def clean(self):
        """Reglas de la contraseña, distintas al crear que al editar."""
        cleaned_data = super().clean()
        es_nuevo = self.instance.pk is None
        nueva_password = cleaned_data.get('nueva_password')
        confirmar_password = cleaned_data.get('confirmar_password')

        # Alta: la contraseña es obligatoria.
        if es_nuevo and not nueva_password:
            self.add_error('nueva_password', 'La contraseña es obligatoria.')

        # Si se escribe alguna contraseña, la confirmación es obligatoria y debe coincidir.
        if nueva_password and nueva_password != confirmar_password:
            self.add_error('confirmar_password', 'Las contraseñas no coinciden.')

        return cleaned_data
    # save() sobrescribe activo a False cuando es_nuevo. 
    # Da igual lo que llegue en el POST: el valor se descarta. 
    # Y activo se queda en el formulario, que es lo que permite que el administrador lo active luego en la edición.
    def save(self, commit=True):
        # es_nuevo se calcula antes de llamar a super().save(commit=False), porque esa llamada puede asignar un pk.
        es_nuevo = self.instance.pk is None
        usuario = super().save(commit=False)

        if es_nuevo:
            # Seguridad: toda cuenta nueva nace inactiva y solo un administrador
            # puede activarla. Se fuerza aqui para que ningun POST lo esquive.
            usuario.activo = False

        nueva_password = self.cleaned_data.get('nueva_password')
        if nueva_password:
            usuario.password = make_password(nueva_password)
        # Si esta vacia, NO tocamos el password actual

        if commit:
            usuario.save()

        return usuario
        
        

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
        # 'password1' y 'password2' no se listan: son campos declarados arriba, no son campos del modelo. Django los incorpora el solo.
        fields = ['nombre', 'apellidos', 'login', 'email', 'telefono']

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


# Usar: python manage.py shell -c "from apps.usuarios.forms import RegistroForm, UsuariosForm; print('OK', sorted(RegistroForm().fields), sorted(UsuariosForm().fields))"
# Deb darnos dos listas: OK ['apellidos', 'email', 'login', 'nombre', 'password1', 'password2', 'telefono'] 
# ['activo', 'apellidos', 'comentarios', 'confirmar_password', 'direccion', 'email', 'login', 'nivel_acceso', 'nombre', 'nueva_password', 'telefono']

#Mas test para comprobar funcionamiento:
#python manage.py shell -c "from apps.usuarios.forms import UsuariosForm; f = UsuariosForm({'nombre':'Test','apellidos':'X','email':'test@x.com','login':'testx','nivel_acceso':1,'nueva_password':'Secreto123','confirmar_password':'Secreto123'}); print(f.is_valid(), f.errors)"    
#python manage.py shell -c "from apps.usuarios.forms import UsuariosForm; f = UsuariosForm({'nombre':'Test','apellidos':'X','email':'test@x.com','login':'testx','nivel_acceso':1,'nueva_password':'Secreto123','confirmar_password':'OtraCosa'}); print(f.is_valid(), f.errors.as_text())"
#python manage.py shell -c "from apps.usuarios.forms import UsuariosForm; f = UsuariosForm({'nombre':'Test','email':'t@x.com','login':'t','nivel_acceso':1}); print(f.is_valid(), f.errors.as_text())"
#python manage.py shell -c "from apps.usuarios.forms import UsuariosForm; f = UsuariosForm({'nombre':'Malo','email':'malo@x.com','login':'malo','nivel_acceso':1,'nueva_password':'Secreto123','confirmar_password':'Secreto123','activo':'on'}); u = f.save(commit=False); print('activo =', u.activo, '| hash =', len(u.password))"
#python manage.py shell -c "from apps.usuarios.forms import RegistroForm; f = RegistroForm({'nombre':'Nuevo','apellidos':'Alta','email':'nuevo@x.com','login':'nuevo','password1':'Secreto123','password2':'Secreto123'}); u = f.save(commit=False); print('form valido =', f.is_valid(), '| activo =', u.activo)"