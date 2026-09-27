from django import forms

from .models import Espacio, Localizacion


class EspacioForm(forms.ModelForm):
    class Meta:
        model = Espacio
        fields = ['nombre', 'descripcion', 'ubicacion']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'ubicacion': 'Ubicación',
        }



class LocalizacionForm(forms.ModelForm):
    class Meta:
        model = Localizacion
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }