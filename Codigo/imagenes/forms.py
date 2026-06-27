"""
Forms para la app Imagenes (F3)
"""
import os
from django import forms
from .models import Imagen


class ImagenForm(forms.ModelForm):
    """Formulario para capturar/subir imagenes."""
    
    archivo = forms.FileField(
        required=False,
        label='Archivo de imagen',
        widget=forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-control'})
    )
    
    class Meta:
        model = Imagen
        fields = ['nombre', 'camara', 'nivel_privacidad', 'comentarios']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre de la imagen', 'class': 'form-control'}),
            'camara': forms.Select(attrs={'class': 'form-control'}),
            'nivel_privacidad': forms.Select(attrs={'class': 'form-control'}),
            'comentarios': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comentarios adicionales', 'class': 'form-control'}),
        }
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            if archivo.size > 50 * 1024 * 1024:  # 50 MB
                raise forms.ValidationError('El archivo es demasiado grande (max 50 MB).')
        return archivo
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            # Guardar el archivo en el directorio Camara/
            directorio = 'Camara'
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            # Generar nombre único
            from django.utils import timezone
            timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
            extension = os.path.splitext(archivo.name)[1]
            nombre_archivo = f"imagen_{timestamp}{extension}"
            
            # Guardar el archivo
            ruta_completa = os.path.join(directorio, nombre_archivo)
            with open(ruta_completa, 'wb') as f:
                for chunk in archivo.chunks():
                    f.write(chunk)
            
            # Guardar la ruta en el modelo
            instance.ruta_archivo = ruta_completa
            instance.tamano = archivo.size
            instance.estado = 'procesada'
        
        if commit:
            instance.save()
        
        return instance
