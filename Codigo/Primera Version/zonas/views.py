
"""
Vistas para la app Zonas (F4 - Gestion de Zonas del Parking)
"""

from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Zona, FicherosDXF
from .forms import ZonaForm, FicherosDXFForm
import json
import os
import sys
import subprocess

# Create your views here.



def lista_zonas(request):
    """
    Lista todas las zonas registradas en el sistema.

    Soporta dos modos de visualización: 'list' (tabla) y 'grid' (tarjetas),
    controlado mediante el parámetro GET 'view'.

    Args:
        request: HttpRequest, puede incluir ?view=list|grid.

    Returns:
        HttpResponse con el template renderizado.
    """
    vista = request.GET.get('view', 'list')
    zonas = Zona.objects.all()
    total_plazas = zonas.filter(tipo__icontains='plaza').count()
    activas = zonas.filter(activo=True).count()
    
    return render(request, 'zonas/lista.html', {
        'zonas': zonas,
        'total_plazas': total_plazas,
        'activas': activas,
        'vista': vista
    })


def registrar_zona(request):
    """
    Registra una nueva zona manualmente a través del formulario ZonaForm.

    Las zonas pueden crearse manualmente (escribiendo coordenadas) o
    importarse desde un DXF. Esta vista cubre el caso manual.

    Args:
        request: HttpRequest (GET muestra formulario, POST procesa).

    Returns:
        HttpResponse con formulario o redirección a lista.
    """
    if request.method == 'POST':
        form = ZonaForm(request.POST, request.FILES)
        if form.is_valid():
            zona = form.save()
            messages.success(request, f'Zona {zona.nombre} registrada correctamente.')
            return redirect('zonas:lista')
    else:
        form = ZonaForm()
    
    return render(request, 'zonas/registro.html', {
        'form': form
    })


def editar_zona(request, pk):
    """
    Edita una zona existente identificada por su primary key.

    Carga la instancia existente y la pasa al formulario para edición.
    Si el formulario es válido, guarda los cambios.

    Args:
        request: HttpRequest.
        pk: Primary key de la zona a editar.

    Returns:
        HttpResponse con formulario pre-rellenado o redirección a lista.
    """
    zona = get_object_or_404(Zona, pk=pk)
    
    if request.method == 'POST':
        form = ZonaForm(request.POST, request.FILES, instance=zona)
        if form.is_valid():
            zona = form.save()
            messages.success(request, f'Zona {zona.nombre} actualizada correctamente.')
            return redirect('zonas:lista')
    else:
        form = ZonaForm(instance=zona)
    
    return render(request, 'zonas/editar.html', {
        'form': form,
        'zona': zona
    })


def eliminar_zona(request, pk):
    """
    Elimina una zona de la base de datos.

    No requiere confirmación POST (eliminación directa GET).
    Para operaciones más seguras considerar cambiar a POST-only.

    Args:
        request: HttpRequest.
        pk: Primary key de la zona a eliminar.

    Returns:
        Redirección a la lista de zonas.
    """
    zona = get_object_or_404(Zona, pk=pk)
    nombre = zona.nombre
    zona.delete()
    messages.success(request, f'Zona {nombre} eliminada.')
    return redirect('zonas:lista')




# ============ Gestion de DXF ============

def lista_dxf(request):
    """
    Lista todos los archivos DXF subidos al sistema.

    Muestra también cuál es el DXF activo actualmente (solo uno puede
    estar activo a la vez para el procesamiento).

    Args:
        request: HttpRequest.

    Returns:
        HttpResponse con el listado de archivos DXF.
    """
    dxf_files = FicherosDXF.objects.all()
    dxf_activo = FicherosDXF.objects.filter(activo=True).first()
    
    return render(request, 'zonas/lista_dxf.html', {
        'dxf_files': dxf_files,
        'dxf_activo': dxf_activo
    })


def registrar_dxf(request):
    """
    Registra (sube) un nuevo archivo DXF al servidor.

    El archivo se almacena en la carpeta 'media/dxf/' mediante el
    FileField del modelo FicherosDXF. El DXF se crea en estado 'pendiente'.

    Args:
        request: HttpRequest (GET formulario, POST procesa).

    Returns:
        HttpResponse con formulario o redirección a lista DXF.
    """
    if request.method == 'POST':
        form = FicherosDXFForm(request.POST, request.FILES)
        if form.is_valid():
            dxf = form.save()
            messages.success(request, f'DXF {dxf.nombre} subido correctamente.')
            return redirect('zonas:lista_dxf')
    else:
        form = FicherosDXFForm()
    
    return render(request, 'zonas/registrar_dxf.html', {
        'form': form
    })


def activar_dxf(request, pk):
    """
    Activa un archivo DXF, desactivando cualquier otro que estuviera activo.

    Solo un DXF puede estar activo a la vez (singleton). Primero se
    desactivan todos mediante update masivo, luego se activa el elegido.
    Esto evita condiciones de carrera al activar/desactivar concurrentemente.

    Args:
        request: HttpRequest.
        pk: Primary key del DXF a activar.

    Returns:
        Redirección a lista DXF.
    """
    dxf = get_object_or_404(FicherosDXF, pk=pk)
    
    # Desactivar todos los demas
    FicherosDXF.objects.filter(activo=True).update(activo=False)
    
    # Activar el seleccionado
    dxf.activo = True
    dxf.save()
    
    messages.success(request, f'DXF {dxf.nombre} activado como activo.')
    return redirect('zonas:lista_dxf')


def procesar_dxf(request, pk):
    """
    Procesa un archivo DXF y genera/actualiza las zonas en la base de datos.

    Flujo de procesamiento:
    1. Verifica que el DXF esté activo (solo se procesa el activo).
    2. Ejecuta el script externo '1_leer_plazas_dxf.py' como subproceso.
    3. Lee el archivo JSON generado por el script.
    4. Para cada elemento del JSON, crea o actualiza una zona en BD.
    5. Mapea las capas del DXF (Plazas, Calzadas, Aceras) a tipos de zona.
    6. Marca el DXF como 'procesado'.

    El script externo se ejecuta como subproceso para aislar errores de
    memoria o DXF corruptos sin afectar al proceso principal de Django.

    Args:
        request: HttpRequest (GET confirmación, POST procesa).
        pk: Primary key del DXF a procesar.

    Returns:
        HttpResponse con confirmación o redirección a lista DXF.
    """
    dxf = get_object_or_404(FicherosDXF, pk=pk)
    
    # Verificar que el DXF está activo
    if not dxf.activo:
        messages.error(request, 'Solo se puede procesar un archivo DXF que esté activo.')
        return redirect('zonas:lista_dxf')
    
    if request.method == 'POST':
        try:
            directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            #De momento no añadimos el codigo del script de viabilidad '1_leer_plazas_dxf', lo adjuntamos a nuestro codigo para ejecutarlo como un hilo de django
            script_dxf = os.path.join(directorio_base, '1_leer_plazas_dxf.py')
            
            if not os.path.exists(script_dxf):
                messages.error(request, f'No se encontro el script')
                return redirect('zonas:lista_dxf')
            
            # Obtener la ruta absoluta
            ruta_dxf = dxf.archivo.path
            
            print(f"[PROCESAR DXF] ruta: {ruta_dxf}")
            
            # Ejecutar el script en hilo  de django
            result = subprocess.run(
                [sys.executable, script_dxf, ruta_dxf],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=directorio_base
            )
            
            print(f"[PROCESAR DXF] return code: {result.returncode}")
            print(f"[PROCESAR DXF] stdout: {result.stdout[:200]}")
            
            if result.returncode != 0:
                messages.error(request, f'Error: {result.stderr[:200]}')
                return redirect('zonas:lista_dxf')
            
            # Leer las plazas generadas por el script en el JSON
            json_plazas = os.path.join(directorio_base, 'auxiliar', '1_plazas_dxf.json')
            
            if not os.path.exists(json_plazas):
                messages.error(request, 'No se genero el archivo de plazas')
                return redirect('zonas:lista_dxf')
            
            if not os.path.exists(json_plazas):
                messages.error(request, 'No se genero el archivo de plazas')
                return redirect('zonas:lista_dxf')
            
            with open(json_plazas, 'r') as f:
                data = json.load(f)
            
            zonas_creadas = 0
            zonas_actualizadas = 0
            
            # Mapear cada plaza del JSON a una zona en BD, determinando el tipo según la capa DXF
            for plaza in data.get('plazas', []):
                nombre_zona = plaza.get('numero', 'Sin numero')
                capa = plaza.get('capa', 'Plazas')
                
                # Determinar el tipo basado en la capa
                tipo = 'plaza'
                if 'Calzadas' in capa:
                    tipo = 'calzada'
                elif 'Aceras' in capa:
                    tipo = 'acera'
                
                zona_existente = Zona.objects.filter(
                    nombre=nombre_zona,
                    tipo=tipo
                ).first()
                
                # Actualizar zona existente con nuevos vértices y centroide
                if zona_existente:
                    zona_existente.vertices = plaza.get('vertices')
                    zona_existente.dxf_origen = dxf
                    if plaza.get('cx') and plaza.get('cy'):
                        zona_existente.centroide = f"{plaza['cx']},{plaza['cy']}"
                    zona_existente.save()
                    zonas_actualizadas += 1
                else:
                    # Crear nueva zona a partir de los datos del DXF
                    Zona.objects.create(
                        nombre=nombre_zona,
                        tipo=tipo,
                        vertices=plaza.get('vertices'),
                        centroide=f"{plaza.get('cx', '')},{plaza.get('cy', '')}" if plaza.get('cx') else '',
                        activo=False,
                        dxf_origen=dxf
                    )
                    zonas_creadas += 1
            
            # Actualizar estado del DXF a procesado
            dxf.estado = 'procesado'
            dxf.save()
            
            messages.success(request, f'DXF procesado: {zonas_creadas} zonas creadas, {zonas_actualizadas} actualizadas.')
            
        except subprocess.TimeoutExpired:
            messages.error(request, 'El procesamiento del DXF tardo demasiado')
        except Exception as e:
            messages.error(request, f'Error al procesar el DXF: {str(e)}')
        
        return redirect('zonas:lista_dxf')
    
    return render(request, 'zonas/procesar_dxf.html', {
        'dxf': dxf
    })


def eliminar_dxf(request, pk):
    """
    Elimina un archivo DXF y todas las zonas asociadas al mismo.

    La eliminación requiere confirmación POST para evitar borrados
    accidentales. Se eliminan también las zonas que dependían de este
    DXF para mantener la integridad de los datos.

    Args:
        request: HttpRequest (GET confirmación, POST elimina).
        pk: Primary key del DXF a eliminar.

    Returns:
        HttpResponse con confirmación o redirección a lista DXF.
    """
    dxf = get_object_or_404(FicherosDXF, pk=pk)
    
    if request.method == 'POST':
        nombre = dxf.nombre
        
        # Eliminar las zonas asociadas a este DXF
        zonas_asociadas = Zona.objects.filter(dxf_origen=dxf)
        zonas_eliminadas = zonas_asociadas.count()
        zonas_asociadas.delete()
        
        # Eliminar el archivo DXF
        dxf.delete()
        
        messages.success(request, f'DXF {nombre} eliminado con {zonas_eliminadas} zonas asociadas.')
        return redirect('zonas:lista_dxf')
    
    return render(request, 'zonas/eliminar_dxf.html', {
        'dxf': dxf,
        'zonas_asociadas': Zona.objects.filter(dxf_origen=dxf).count(),
        'zonas_lista': Zona.objects.filter(dxf_origen=dxf)
    })
    
def debug_dxf(request, pk):
    """
    Página de depuración para procesar DXF paso a paso y aplicar reglas.

    Muestra información detallada del proceso:
    - Estado del DXF en BD y del archivo físico
    - Existencia y ubicación del script de procesamiento
    - Salida completa del script (stdout, stderr)
    - JSON generado y zonas resultantes
    - Aplicación interactiva de reglas de activación/desactivación

    Es una herramienta de diagnóstico para verificar que el DXF se
    procesa correctamente antes de usar el flujo normal.

    Args:
        request: HttpRequest (GET muestra info, POST ejecuta).
        pk: Primary key del DXF a depurar.

    Returns:
        HttpResponse con información detallada de depuración.
    """
    import sys
    dxf = get_object_or_404(FicherosDXF, pk=pk)
    
    debug_info = []
    directorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    debug_info.append(f"1. DXF en BD: {dxf.nombre}")
    debug_info.append(f"   - Activo: {dxf.activo}")
    debug_info.append(f"   - Archivo: {dxf.archivo}")
    
    # Operadores disponibles para reglas
    OPERADORES = [
        ('==', 'Igual a'),
        ('!=', 'Diferente de'),
    ]
    
    # Obtener tipos únicos de zonas existentes en la BD
    tipos_zonas = list(set(Zona.objects.values_list('tipo', flat=True)))
    
    # Si no hay zonas en BD, leer capas del DXF directamente
    if not tipos_zonas:
        from zonas.reglas import obtener_capas
        try:
            ruta_dxf = dxf.archivo.path
            tipos_zonas = obtener_capas(ruta_dxf)
        except:
            pass
    
    # Intentar obtener la ruta
    try:
        ruta_archivo = dxf.archivo.path
        debug_info.append(f"   - .path: {ruta_archivo}")
    except Exception as e:
        debug_info.append(f"   - .path ERROR: {e}")
        ruta_archivo = None
    
    # Verificar si existe
    if ruta_archivo and os.path.exists(ruta_archivo):
        debug_info.append(f"   - EXISTE: SI")
    else:
        debug_info.append(f"   - EXISTE: NO")
    
    # Verificar script
    script_dxf = os.path.join(directorio_base, '1_leer_plazas_dxf.py')
    debug_info.append(f"2. Script: {script_dxf}")
    debug_info.append(f"   - Existe: {os.path.exists(script_dxf)}")
    
    # Si se envió el formulario, procesar
    resultado = None
    if request.method == 'POST':
        debug_info.append("3. Ejecutando script...")
        
        if ruta_archivo and os.path.exists(ruta_archivo):
            result = subprocess.run(
                [sys.executable, script_dxf, ruta_archivo],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=directorio_base
            )
            debug_info.append(f"   - Return code: {result.returncode}")
            
            if result.stdout:
                for line in result.stdout.split('\n'):
                    debug_info.append(f"   - STDOUT: {line}")
            
            if result.stderr:
                debug_info.append(f"   - STDERR: {result.stderr}")
            
            # Leer JSON
            json_plazas = os.path.join(directorio_base, 'auxiliar', '1_plazas_dxf.json')
            if os.path.exists(json_plazas):
                with open(json_plazas, 'r') as f:
                    data = json.load(f)
                debug_info.append(f"4. Plazas generadas: {len(data.get('plazas', []))}")
                
                # Importar a BD
                zonas_creadas = 0
                for plaza in data.get('plazas', []):
                    nombre_zona = plaza.get('numero', 'Sin numero')
                    capa = plaza.get('capa', 'Plazas')
                    tipo = capa
                    
                    cx = plaza.get('cx')
                    cy = plaza.get('cy')
                    centroide = f"{cx},{cy}" if cx and cy else ''
                    
                    Zona.objects.update_or_create(
                        nombre=nombre_zona,
                        tipo=tipo,
                        defaults={
                            'vertices': plaza.get('vertices'),
                            'centroide': centroide,
                            'dxf_origen': dxf,
                            'activo': False
                        }
                    )
                    zonas_creadas += 1
                
                debug_info.append(f"5. Zonas importadas a BD: {zonas_creadas}")
                resultado = f"OK - {zonas_creadas} zonas"
                
                # Aplicar regla de activación
                operador = request.POST.get('operador')
                valor = request.POST.get('valor')
                accion = request.POST.get('accion')
                
                if operador and valor and accion:
                    from zonas.reglas import aplicar_reglas_zonas
                    debug_info.append(f"6. Aplicando regla: {operador} {valor} -> {accion}")
                    aplicar_reglas_zonas(operador, valor, accion)
                    debug_info.append("   - Regla aplicada")
            else:
                debug_info.append("4. ERROR: No se generó JSON")
        else:
            debug_info.append("3. ERROR: Ruta de archivo no válida")
    
    return render(request, 'zonas/debug_dxf.html', {
        'dxf': dxf,
        'debug_info': debug_info,
        'resultado': resultado,
        'zonas_lista': Zona.objects.filter(dxf_origen=dxf),
        'tipos_zonas': tipos_zonas,
        'operadores': OPERADORES
    })
