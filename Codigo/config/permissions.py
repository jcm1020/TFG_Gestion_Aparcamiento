from django.contrib import messages
from django.shortcuts import redirect

# Cambiamos el sistema de seguridad anteriormente implementado, mas inseguro y con mas codigo.
# Ahora si un administrador degrada a un usuario de nivel 2 a nivel 1, 
# el cambio surte efecto en su siguiente peticion, sin esperar a que cierre sesion.

# Usaremos a partir de ahora el modulo functools, forma canónica de escribir decoradores en Python.
# Como no utilizamos el login de Django toca escribir a mano el decorador con el control de seguridad personalizado, 
# segun investigue esto lo que se hace cuando la autenticacion es propia
from functools import wraps  


# Constante con el nivel de acceso que concede permisos de administrador.
# Se define aqui para no repetir el numero 2 por todo el codigo.
NIVEL_ADMINISTRADOR = 2

def usuario_activo(request):
    """
    Devuelve el usuario de la sesion si esta correctamente autenticado, o None si no lo esta.
    """
    

    #El import de Usuarios esta dentro de la funcion a proposito
    #(import perezoso). Asi este archivo no depende de ninguna app
    #concreta al importarse, y se evita riesgos de importacion    
    from apps.usuarios.models import Usuarios
    
    # Se comprueba SIEMPRE contra la base de datos, no se fia de lo que dice la sesion. 
    # Es una medida de seguridad:  si un administrador desactiva o degrada a un usuario, 
    # el cambio surte efecto en la siguiente peticion, sin esperar a que cierre sesion ni a que expire la cookie.
    usuario_id = request.session.get('usuario_id')
    
    
    # La clave 'usuario_id' es la que login_view() guarda al iniciar sesion.
    if not usuario_id:
        return None # 'None' significa: no hay sesion, o el usuario fue borrado, o el usuario esta marcado como inactivo.
    
    # .filter() en lugar de .get(): no lanza excepcion si no hay resultados, simplemente devuelve None, que es justo lo que queremos hacer.
    return Usuarios.objects.filter(pk=usuario_id, activo=True,).first()



# El proyecto NO usa el sistema de autenticacion estandar de Django (el que tiene un AUTH_USER_MODEL propio). 
# El login es manual: al iniciar sesion, login_view() guarda tres claves en la sesion:
    # request.session['usuario_id']    -> pk del usuario
    # request.session['usuario_login'] -> nombre de login
    # request.session['usuario_nivel'] -> 1 (Basico) o 2 (Administrador)
def actualizar_sesion(request, usuario):
    """
    Refresca los datos del usuario guardados en la sesion.

    Se llama en cada peticion protegida. Su trabajo es que la sesion no
    se quede con datos obsoletos: si el usuario cambia de nivel de
    acceso o de nombre, la sesion se entera en la siguiente pagina en
    lugar de conservar el valor antiguo hasta que expire la cookie.
    """
    request.session['usuario_id'] = usuario.pk
    request.session['usuario_login'] = usuario.login
    request.session['usuario_nivel'] = usuario.nivel_acceso

'''
=============================================================
TRES NIVELES DE USO
=============================================================
Una vista publica                           (login, registro, portada). Sin decorador.
Una vista de lectura o escritura general    @sesion_requerida. Cualquier usuario autenticado, sea del nivel que sea.
Una vista de escritura protegida            @administrador_requerida. Solo nivel 2.

Ademas, las vistas que BORRAN datos (eliminar) llevan encima
@require_POST de django.views.decorators.http, que rechaza el GET.
'''
def sesion_requerida(vista):
    """
    Decorador de SOLO LECTURA Y ESCRITURA GENERAL.

    Permite el acceso a cualquier usuario que tenga una sesion valida.
    Lo usan las vistas, que no modifican datos sensibles.

    Si no hay sesion, o el usuario esta inactivo:
      1. Se borra la sesion con flush().
      2. Se redirige al login.
    """
    @wraps(vista)
    def wrapper(request, *args, **kwargs):
        usuario = usuario_activo(request)

        if usuario is None:
            # flush() no es lo mismo que clear(). flush() destruye la sesion actual y genera un identificador nuevo. 
            # Esto evita ataques de modificacion de sesion
            request.session.flush()
            return redirect('usuarios:login')

        actualizar_sesion(request, usuario)
        
        # *args y **kwargs se reenvian sin tocarlos para que la vista siga recibiendo sus parametros (por ejemplo, el pk de la URL).
        return vista(request, *args, **kwargs)

    return wrapper


def administrador_requerida(vista):
    """
    Decorador de ESCRITURA PROTEGIDA.

    Mas estricto que sesion_requerida: exige nivel de acceso 2.
    Lo usan las vistas de crear, editar y eliminar, tanto de usuarios como otras vistas seleccionadas.

    Si no hay sesion, o el usuario esta inactivo:
      1. Se borra la sesion con flush().
      2. Se redirige al login.

    Si hay sesion pero el nivel no es 2:
      1. Se registra un mensaje de error para que se muestre en la pagina.
      2. Se redirige al dashboard, que es donde ese usuario puede trabajar.

    Aunque el usuario escriba la URL a mano, la vista no llegara a ejecutarse. 
    
    Nota: Lo que hacen los '{% if %}' de las plantillas es solo esconder el boton, por comodidad.
    """
    @wraps(vista)
    def wrapper(request, *args, **kwargs):
        usuario = usuario_activo(request)

        if usuario is None:
            request.session.flush()
            return redirect('usuarios:login')

        if usuario.nivel_acceso != NIVEL_ADMINISTRADOR:
            messages.error(request, 'Solo los administradores pueden realizar esta acción.',)
            return redirect('dashboard')

        actualizar_sesion(request, usuario)
        return vista(request, *args, **kwargs)

    return wrapper