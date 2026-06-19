"""
Vistas para la app Imagenes (F3 - Gestion de Imagenes)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Imagen
from .forms import ImagenForm
import os

# Create your views here.


def lista_imagenes(request):
    """Lista todas las imagenes capturadas."""
    vista = request.GET.get('view', 'list')
    imagenes = Imagen.objects.all()
    pendientes = imagenes.filter(estado='pendiente').count()
    procesadas = imagenes.filter(estado='procesada').count()
    
    return render(request, 'imagenes/lista.html', {
        'imagenes': imagenes,
        'pendientes': pendientes,
        'procesadas': procesadas,
        'total': imagenes.count(),
        'vista': vista
    })


def subir_imagen(request):
    """Permite subir una nueva imagen."""
    if request.method == 'POST':
        form = ImagenForm(request.POST, request.FILES)
        if form.is_valid():
            imagen = form.save()
            messages.success(request, f'Imagen {imagen.nombre} guardada correctamente.')
            return redirect('imagenes:lista')
    else:
        form = ImagenForm()
    
    return render(request, 'imagenes/subir.html', {
        'form': form
    })


def eliminar_imagen(request, pk):
    """Elimina una imagen."""
    try:
        imagen = Imagen.objects.get(pk=pk)
        nombre = imagen.nombre
        ruta_archivo = imagen.ruta_archivo
        
        # Eliminar archivo físico si existe
        if ruta_archivo and os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
                # Eliminar registro de la base de datos        
                imagen.delete()
                messages.success(request, f'Imagen {nombre} eliminada.')
            except Exception as e:
                # Loguear error y no continuar con la eliminación del registro
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al eliminar archivo {ruta_archivo}: {e}")        
        
        
    except Imagen.DoesNotExist:
        messages.error(request, 'Imagen no encontrada.')
    
    return redirect('imagenes:lista')


def marcar_referencia(request, pk):
    """Marca una imagen como referencia."""
    imagen = get_object_or_404(Imagen, pk=pk)
    
    # Desmarcar todas las demás
    Imagen.objects.update(es_referencia=False)
    
    # Marcar la seleccionada
    imagen.es_referencia = True
    imagen.save()
    
    messages.success(request, f'Imagen "{imagen.nombre}" marcada como referencia.')
    return redirect('imagenes:lista')


def eliminar_todas(request):
    """Elimina todas las imágenes y archivos del disco."""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        logger.warning("ELIMINAR_TODAS - Iniciando borrado de imagenes...")
        
        # Contar imágenes antes de borrar
        count = Imagen.objects.count()
        logger.warning(f"ELIMINAR_TODAS - Imagenes a borrar: {count}")
        
        # Eliminar registros de la base de datos
        Imagen.objects.all().delete()
        
        # Eliminar archivos del directorio Camara/
        if os.path.exists('Camara'):
            archivos_camara = os.listdir('Camara')
            logger.warning(f"ELIMINAR_TODAS - Archivos en Camara antes: {len(archivos_camara)}")
            for f in archivos_camara:
                try:
                    os.remove(os.path.join('Camara', f))
                    logger.warning(f"ELIMINAR_TODAS - Borrado: {f}")
                except Exception as e:
                    logger.warning(f"ELIMINAR_TODAS - Error borrando {f}: {e}")
        
        # Eliminar archivos del directorio imagenes_procesadas/
        if os.path.exists('imagenes_procesadas'):
            for f in os.listdir('imagenes_procesadas'):
                try:
                    os.remove(os.path.join('imagenes_procesadas', f))
                except:
                    pass
        
        messages.success(request, f'{count} imágenes eliminadas.')
    
    return redirect('imagenes:lista')