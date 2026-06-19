"""
Forms para la app Camaras (F2)
"""
from django import forms
from .models import Camara


class CamaraForm(forms.ModelForm):
    """Formulario para crear/editar camaras."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contrasena'}),
        required=False,
        help_text='Dejar en blanco para mantener la actual.'
    )
    
    class Meta:
        model = Camara
        fields = [
            'nombre', 'ip', 'puerto', 'usuario', 'password',
            'ubicacion_fisica', 'zona_aparcamiento', 'resolucion',
            'url_stream_isapi', 'estado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la camara'}),
            'ip': forms.TextInput(attrs={'placeholder': '192.168.1.100'}),
            'puerto': forms.NumberInput(attrs={'placeholder': '554'}),
            'usuario': forms.TextInput(attrs={'placeholder': 'Usuario de conexion'}),
            'ubicacion_fisica': forms.TextInput(attrs={'placeholder': 'Ubicacion fisica'}),
            'zona_aparcamiento': forms.TextInput(attrs={'placeholder': 'Zona del parking'}),
            'resolucion': forms.TextInput(attrs={'placeholder': '1920x1080'}),
            'url_stream_isapi': forms.TextInput(attrs={'placeholder': 'http://{ip}/ISAPI/Streaming/channels/101/picture'}),
        }
    
    def clean_ip(self):
        ip = self.cleaned_data.get('ip')
        if self.instance.pk:
            if Camara.objects.filter(ip=ip).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Ya existe una camara con esta IP.')
        else:
            if Camara.objects.filter(ip=ip).exists():
                raise forms.ValidationError('Ya existe una camara con esta IP.')
        return ip
