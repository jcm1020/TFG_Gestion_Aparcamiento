from django.shortcuts import render

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST

from config.permissions import administrador_requerida, sesion_requerida

from .forms import EspacioForm, LocalizacionForm
from .models import Espacio, Localizacion


# Create your views here.


def contexto_lista(request):
    vista = request.GET.get('view', 'list')

    if vista not in ('grid', 'list'):
        vista = 'list'

    espacios = Espacio.objects.all()

    total = espacios.count()
    con_ubicacion = espacios.exclude(ubicacion='').count()
    sin_ubicacion = total - con_ubicacion
    
    #localizacion = Localizacion.objects.get_or_create(pk=1) # error
    # Es una tupla
    localizacion, created = Localizacion.objects.get_or_create(pk=1, defaults={'nombre': 'Localización sin configurar'},)

    return {
        'espacios': espacios,
        'vista': vista,
        'total': total,
        'con_ubicacion': con_ubicacion,
        'sin_ubicacion': sin_ubicacion,
        'localizacion': localizacion,
        'localizacion_form': LocalizacionForm(instance=localizacion),
    }


@sesion_requerida
def lista_espacios(request):
    return render(request, 'espacios/lista.html', contexto_lista(request), )


@administrador_requerida
@require_POST
def editar_localizacion(request):
    
    # localizacion = Localizacion.objects.get_or_create(pk=1)
    # Mejor asi para proteger el singleton
    localizacion, created = Localizacion.objects.get_or_create(pk=1, defaults={'nombre': 'Localización sin configurar'},)
    form = LocalizacionForm(request.POST, instance=localizacion)

    if form.is_valid():
        form.save()
        messages.success(request, 'Localización actualizada correctamente.')
        return redirect('espacios:lista')

    contexto = contexto_lista(request)
    contexto['localizacion_form'] = form

    return render(request, 'espacios/lista.html', contexto, )


@administrador_requerida
@require_http_methods(['GET', 'POST'])
def crear_espacio(request):
    if request.method == 'POST':
        form = EspacioForm(request.POST)

        if form.is_valid():
            espacio = form.save()
            messages.success(request, f'Espacio {espacio.nombre} creado correctamente.',)
            return redirect('espacios:lista')
    else:
        form = EspacioForm()

    return render(request, 'espacios/crear.html', {'form': form},  )


@administrador_requerida
@require_http_methods(['GET', 'POST'])
def editar_espacio(request, pk):
    espacio = get_object_or_404(Espacio, pk=pk)

    if request.method == 'POST':
        form = EspacioForm(request.POST, instance=espacio)

        if form.is_valid():
            espacio = form.save()
            messages.success(request, f'Espacio {espacio.nombre} actualizado correctamente.',)
            return redirect('espacios:lista')
    else:
        form = EspacioForm(instance=espacio)

    return render(request, 'espacios/editar.html', {'form': form, 'espacio': espacio,}, )


@administrador_requerida
@require_POST
def eliminar_espacio(request, pk):
    espacio = get_object_or_404(Espacio, pk=pk)
    nombre = espacio.nombre

    espacio.delete()

    messages.success(request, f'Espacio {nombre} eliminado correctamente.')
    return redirect('espacios:lista')

