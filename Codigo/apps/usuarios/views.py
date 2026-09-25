from django.shortcuts import render

from .models import Usuarios
from .forms import UsuariosForm, RegistroForm, LoginForm

from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password


# Create your views here.

# Vista index (Home)
def index(request):
    return render(request, 'index.html')
    
# Vista login
#def login(request):
#    return render(request, 'login/login.html')
    
# Vista registro
#def registro(request):
#    return render(request, 'login/registro.html')
    
    
    
"""
Vistas para la app Usuarios (1 - Gestion de Usuarios del sistema)
"""

def registro_view(request):
    """Vista para registro de nuevos usuarios."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        # Los metodos clean() se llaman automaticamente en form.is_valid()
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                login = form.cleaned_data['login']

                usuario = form.save(commit=False)
                password = form.cleaned_data.get('password1')
                """
                Contraseña del usuario, ALMACENADA COMO HASH (no texto plano).
    
                🔒 SEGURIDAD IMPORTANTE:
                - Django usa por defecto 'make_password()' que aplica PBKDF2-SHA256
                - Nunca se almacena la contraseña en texto legible
                - Al crear/editar, usar make_password() desde views.py
    
                Ejemplo de creación segura:
                >>> from django.contrib.auth.hashers import make_password
                >>> password_hash = make_password('mi_contra_segura123')
                >>> user.password = password_hash
                >>> user.save()
    
                Verificación de contraseña:
                >>> from django.contrib.auth.hashers import check_password
                >>> check_password('mi_contra_segura123', password_hash)  # Retorna True/False
    
                Longitud de 255 caracteres cubre:
                - PBKDF2-SHA256 (más rápido, recomendado para apps web simples)
                - Argon2 y bcrypt (más lento, pero más seguros para apps críticas)
    
                Nunca mostrar password en logs o errores.
                """
                usuario.password = make_password(password)
                usuario.login = form.cleaned_data.get('login')
                #usuario.nivel_acceso = 1  # Nivel basico por defecto
                # Primer usuario del sistema → administrador; el resto → básico
                if Usuarios.objects.count() == 0:
                    usuario.nivel_acceso = 2  # Administrador
                else:
                    usuario.nivel_acceso = 1  # Nivel básico por defecto
                usuario.save()

                # Verificacion opcional (solo desarrollo): comprobar el hash guardado
                # check_password(password, Usuarios.objects.get(login=login).password)

                messages.success(request, 'Usuario creado correctamente. Inicia sesión.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f'Error al crear usuario: {str(e)}')
                form = RegistroForm()
    else:
        form = RegistroForm()

    return render(request, 'login/registro.html', {'form': form})

def login_view(request):
    """Vista de inicio de sesion con sesion manual."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember', False)

            try:
                usuario = Usuarios.objects.get(login=username)
                """
                Contraseña del usuario, ALMACENADA COMO HASH (no texto plano).
    
                🔒 SEGURIDAD IMPORTANTE:
                - Django usa por defecto 'make_password()' que aplica PBKDF2-SHA256
                - Nunca se almacena la contraseña en texto legible
                - Al crear/editar, usar make_password() desde views.py
    
                Ejemplo de creación segura:
                >>> from django.contrib.auth.hashers import make_password
                >>> password_hash = make_password('mi_contra_segura123')
                >>> user.password = password_hash
                >>> user.save()
    
                Verificación de contraseña:
                >>> from django.contrib.auth.hashers import check_password
                >>> check_password('mi_contra_segura123', password_hash)  # Retorna True/False
    
                Longitud de 255 caracteres cubre:
                - PBKDF2-SHA256 (más rápido, recomendado para apps web simples)
                - Argon2 y bcrypt (más lento, pero más seguros para apps críticas)
    
                Nunca mostrar password en logs o errores.
                """
                if check_password(password, usuario.password) and usuario.activo:
                    # Gestionar sesion manualmente
                    request.session['usuario_id'] = usuario.pk
                    request.session['usuario_login'] = usuario.login
                    request.session['usuario_nivel'] = usuario.nivel_acceso

                    # Recordarme: sesion duradera
                    if not remember:
                        request.session.set_expiry(0)

                    return redirect('dashboard')
                else:
                    form.add_error(None, 'Usuario o contraseña incorrectos')
            except Usuarios.DoesNotExist:
                form.add_error(None, 'Usuario o contraseña incorrectos')

    else:
        form = LoginForm()

    return render(request, 'login/login.html', {'form': form})

def logout_view(request):
    """Cierra la sesion del usuario."""
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')

def lista_usuarios(request):
    """Lista todos los usuarios del sistema."""
    # 1. Parametro 'view' de la URL (ej: ?view=grid). Por defecto 'list'
    vista = request.GET.get('view', 'list')

    # 2. Obtiene todos los usuarios
    usuarios = Usuarios.objects.all()

    # 3. Calcula totales y contadores
    total = usuarios.count()
    activos = usuarios.filter(activo=True).count()
    inactivos = total - activos

    # 4. Cuenta usuarios por nivel de acceso
    nivel_basico = usuarios.filter(nivel_acceso=1).count()
    nivel_admin = usuarios.filter(nivel_acceso=2).count()

    # 5. Renderiza la plantilla con todos los datos
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'vista': vista,
        'total': total,
        'activos': activos,
        'inactivos': inactivos,
        'nivel_basico': nivel_basico,
        'nivel_admin': nivel_admin,
    })

def crear_usuario(request):
    """Crea un nuevo usuario del sistema (solo para administradores)."""
    
    if request.session.get('usuario_nivel', 0) != 2:
        messages.error(request, 'Solo los administradores pueden crear usuarios.')
        return redirect('usuarios:lista')

    if request.method == 'POST':
        form = UsuariosForm(request.POST)

        if form.is_valid():
            # Recuperar email/login y verificar duplicados antes de guardar
            email = form.cleaned_data.get('email')
            login = form.cleaned_data.get('login')

            if Usuarios.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está registrado.')
                return render(request, 'usuarios/crear.html', {'form': form})

            if Usuarios.objects.filter(login=login).exists():
                form.add_error('login', 'Este nombre de usuario ya está en uso.')
                return render(request, 'usuarios/crear.html', {'form': form})

            # Guarda en memoria pero no en BD todavia
            usuario = form.save(commit=False)

            # Procesa la contraseña
            password = form.cleaned_data.get('nueva_password')
            if password:
                usuario.password = make_password(password)  # Hashea la contraseña
            else:
                usuario.password = make_password('changeme123')  # Default si no puso nada

            usuario.save()

            messages.success(request, f'Usuario {usuario.nombre} creado correctamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuariosForm()

    return render(request, 'usuarios/crear.html', {'form': form})
    
    

def editar_usuario(request, pk):
    """Edita un usuario existente (solo administradores)."""
    
    if request.session.get('usuario_nivel', 0) != 2:
        messages.error(request, 'Solo los administradores pueden editar usuarios.')
        return redirect('usuarios:lista')

    usuario = get_object_or_404(Usuarios, pk=pk)

    if request.method == 'POST':
        form = UsuariosForm(request.POST, instance=usuario)

        if form.is_valid():
            # Recuperar email/login y verificar duplicados antes de guardar (excluyendo el propio usuario)
            email = form.cleaned_data.get('email')
            login = form.cleaned_data.get('login')
            if Usuarios.objects.filter(email=email).exclude(pk=pk).exists():
                form.add_error('email', 'Este correo electrónico ya está registrado.')
                return render(request, 'usuarios/editar.html', {'form': form, 'usuario': usuario})
            if Usuarios.objects.filter(login=login).exclude(pk=pk).exists():
                form.add_error('login', 'Este nombre de usuario ya está en uso.')
                return render(request, 'usuarios/editar.html', {'form': form, 'usuario': usuario})

            # Guarda en memoria sin commit
            usuario = form.save(commit=False)

            # Solo actualiza password si se proporciono una nueva
            nueva_password = form.cleaned_data.get('nueva_password')
            if nueva_password:
                usuario.password = make_password(nueva_password)
            # Si esta vacio, NO tocamos el password actual

            usuario.save()

            messages.success(request, f'Usuario {usuario.nombre} actualizado correctamente.')
            return redirect('usuarios:lista')
    else:
        form = UsuariosForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {
        'form': form,
        'usuario': usuario
    })
    
    
def eliminar_usuario(request, pk):
    """Elimina un usuario (solo administradores).""" 
    
    if request.session.get('usuario_nivel', 0) != 2:
        messages.error(request, 'Solo los administradores pueden eliminar usuarios.')
        return redirect('usuarios:lista')

    usuario = get_object_or_404(Usuarios, pk=pk)
    nombre = usuario.nombre
    usuario.delete()

    messages.success(request, f'Usuario {nombre} eliminado correctamente.')
    return redirect('usuarios:lista')


