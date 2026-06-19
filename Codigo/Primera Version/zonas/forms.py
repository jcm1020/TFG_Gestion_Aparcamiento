"""
Forms para la app Zonas (F4)
"""
from django import forms
from .models import Zona, FicherosDXF


class ZonaForm(forms.ModelForm):
    """Formulario para registrar zonas."""
    
    tipo = forms.ChoiceField(choices=[], required=False)
    
    class Meta:
        model = Zona
        fields = [
            'nombre', 'tipo', 'tag', 'coordenadas_posicion',
            'ancho', 'largo', 'rotacion', 'centroide',
            'vertices', 'camara_asignada', 'activo'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la zona'}),
            'tag': forms.TextInput(attrs={'placeholder': 'Etiqueta manual (opcional)'}),
            'coordenadas_posicion': forms.TextInput(attrs={'placeholder': 'X, Y'}),
            'ancho': forms.NumberInput(attrs={'placeholder': '2.5', 'step': '0.1'}),
            'largo': forms.NumberInput(attrs={'placeholder': '5.0', 'step': '0.1'}),
            'rotacion': forms.NumberInput(attrs={'placeholder': '0', 'step': '0.1'}),
            'centroide': forms.TextInput(attrs={'placeholder': 'Xc, Yc'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar tipos únicos de la BD
        tipos = list(set(Zona.objects.values_list('tipo', flat=True)))
        choices = [('', '---------')] + [(t, t) for t in tipos]
        self.fields['tipo'].choices = choices


class FicherosDXFForm(forms.ModelForm):
    """Formulario para subir archivos DXF."""
    
    class Meta:
        model = FicherosDXF
        fields = ['nombre', 'archivo', 'escala', 'unidad_medida']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre del archivo DXF'}),
            'archivo': forms.FileInput(attrs={'accept': '.dxf'}),
            'escala': forms.TextInput(attrs={'placeholder': '1:100'}),
        }