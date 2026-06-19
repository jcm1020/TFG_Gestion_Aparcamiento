"""
Vistas para la app Camaras (F2 - Gestion de Camaras)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Camara
from .forms import CamaraForm
from .capturador import iniciar_captura, detener_captura, esta_capturando

# Create your views here.

def lista_camaras(request):
    """
    Lista todas las cámaras registradas en el sistema.

    Calcula contadores de estado (online/offline) para mostrar en
    las cards de estadísticas de la cabecera de la vista.
    Soporta cambio de visualización entre 'grid' y 'list'.

    Args:
        request: HttpRequest, puede incluir ?view=list|grid.

    Returns:
        HttpResponse renderizado con lista de cámaras y contadores.
    """
    vista = request.GET.get('view', 'list')
    camaras = Camara.objects.all()
    online_count = camaras.filter(estado='online').count()
    offline_count = camaras.filter(estado='offline').count()
    
    return render(request, 'camaras/lista.html', {
        'camaras': camaras,
        'online_count': online_count,
        'offline_count': offline_count,
        'total_count': camaras.count(),
        'vista': vista
    })


def crear_camara(request):
    """
    Crea una nueva cámara en el sistema.

    La contraseña se maneja de forma separada del formulario:
    se asigna manualmente al campo 'password' del modelo y NO se
    almacena como parte del hash de Django (se guarda en texto plano
    porque se necesita la contraseña original para la autenticación
    HTTP Digest con la cámara).

    Args:
        request: HttpRequest (GET muestra formulario, POST procesa).

    Returns:
        HttpResponse con formulario o redirección a lista de cámaras.
    """
    if request.method == 'POST':
        form = CamaraForm(request.POST)
        if form.is_valid():
            camara = form.save(commit=False)
            # Extraer la contraseña del formulario (campo independiente del modelo)
            password = form.cleaned_data.get('password')
            if password:
                camara.password = password
            camara.save()
            messages.success(request, f'Camara {camara.nombre} creada correctamente.')
            return redirect('camaras:lista')
    else:
        form = CamaraForm()
    
    return render(request, 'camaras/crear.html', {
        'form': form
    })


def editar_camara(request, pk):
    """
    Edita una cámara existente identificada por su primary key.

    Solo actualiza la contraseña si se proporciona una nueva en el
    formulario. Si el campo password queda vacío, se mantiene la
    contraseña anterior sin modificar.

    Args:
        request: HttpRequest.
        pk: Primary key de la cámara a editar.

    Returns:
        HttpResponse con formulario pre-rellenado o redirección a lista.
    """
    camara = get_object_or_404(Camara, pk=pk)
    
    if request.method == 'POST':
        form = CamaraForm(request.POST, instance=camara)
        if form.is_valid():
            camara = form.save(commit=False)
            # Solo actualizar la contraseña si el usuario introdujo una nueva
            password = form.cleaned_data.get('password')
            if password:
                camara.password = password
            camara.save()
            messages.success(request, f'Camara {camara.nombre} actualizada correctamente.')
            return redirect('camaras:lista')
    else:
        form = CamaraForm(instance=camara)
    
    return render(request, 'camaras/editar.html', {
        'form': form,
        'camara': camara
    })


def eliminar_camara(request, pk):
    """
    Elimina una cámara del sistema.

    Antes de eliminar, detiene cualquier captura activa asociada a
    la cámara para evitar que el hilo de captura intente acceder a
    un registro que ya no existe en la base de datos.

    Args:
        request: HttpRequest.
        pk: Primary key de la cámara a eliminar.

    Returns:
        Redirección a la lista de cámaras.
    """
    camara = get_object_or_404(Camara, pk=pk)
    nombre = camara.nombre
    # Detener captura activa antes de eliminar para evitar hilos huérfanos
    detener_captura(pk)
    camara.delete()
    messages.success(request, f'Camara {nombre} eliminada correctamente.')
    return redirect('camaras:lista')


def toggle_captura(request, pk):
    """
    Inicia o detiene la captura continua de imágenes de una cámara.

    Funciona como un interruptor (toggle): si la cámara está capturando,
    la detiene; si no está capturando, la inicia.
    Redirige a la página anterior (HTTP_REFERER) para no perder el contexto
    de navegación del usuario.

    Args:
        request: HttpRequest.
        pk: Primary key de la cámara.

    Returns:
        Redirección a la página anterior o a la lista de cámaras.
    """
    camara = get_object_or_404(Camara, pk=pk)

    if esta_capturando(pk):
        detener_captura(pk)
        messages.info(request, f'Captura detenida para {camara.nombre}.')
    else:
        iniciar_captura(pk)
        messages.success(request, f'Captura iniciada para {camara.nombre}.')
    
    # Redirigir a la página desde la que se hizo clic (HTTP_REFERER)
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('camaras:lista')
