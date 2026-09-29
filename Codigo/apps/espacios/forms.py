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
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Plaza A-1',
                    'maxlength': 100,
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Descripción y notas del espacio',
                }
            ),
            'ubicacion': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Planta 1, Sector A o coordenadas',
                    'maxlength': 100,
                }
            ),
        }


class LocalizacionForm(forms.ModelForm):
    class Meta:
        model = Localizacion
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
        }
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'placeholder': 'Ej: Aparcamiento Universidad de Burgos',
                    'maxlength': 200,
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Descripción opcional de la localización',
                }
            ),
        }