"""
Vistas para la app Camaras (F1 - Gestion de Usuarios del Nucleo)
"""
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404  #Añadido
from django.contrib import messages  #Añadido
#from django.contrib.auth.hashers import make_password  #Añadido
from django.contrib.auth.hashers import make_password, check_password  #Añadido
from .models import UsuarioNucleo   #Añadido
from .forms import UsuarioNucleoForm   #Añadido  
from .forms_auth import RegistroForm, LoginForm  #Añadido


# Create your views here.

def registro_view(request):
    """Vista para registro de nuevos usuarios."""
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        #Los métodos clean() en Django se llaman automáticamente durante form.is_valid(). 
        if form.is_valid():            
            # Crear usuario con password hasheada
            # Redirigir a login
            try:
                email = form.cleaned_data['email']
                login = form.cleaned_data['login']
                
                '''
                if UsuarioNucleo.objects.filter(email=form.cleaned_data['email']).exists():
                    messages.error(request, 'Este email ya está registrado.')
                    return render(request, 'registration/registro.html', {'form': form})
                    
                if UsuarioNucleo.objects.filter(login=login).exists():
                    messages.error(request, 'Este nombre de usuario ya está registrado.')
                    return render(request, 'registration/registro.html', {'form': form})
                '''    
                usuario = form.save(commit=False)
                password = form.cleaned_data.get('password1')
                usuario.password = make_password(password)
                #Esto no funcionaba no se guardaba bien el login del usuario
                #usuario.login = usuario.email.split('@')[0]  # login = parte antes de @
                usuario.login = form.cleaned_data.get('login')
                usuario.nivel_acceso = 1  # Nivel básico por defecto
                usuario.save()
                
                #Verificacion
                usuario_guardado = UsuarioNucleo.objects.get(login=login)
                verifica = check_password(password, usuario_guardado.password)
                print(f"✓ Verificación post-guardado: {verifica}")
                
                #Quitar en produccion solo para comprobaciones actuales
                password = form.cleaned_data.get('password1')
                #print(f"DEBUG - Password recibido: {password}")  # OJO: muestra la contraseña en consola!
                #print(f"DEBUG - Password hash generado: {make_password(password)}")
                
                messages.success(request, 'Usuario creado correctamente. Inicia sesión.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error al crear usuario: {str(e)}')
                form = RegistroForm()
    else:
        form = RegistroForm()
        
    return render(request, 'registration/registro.html', {'form': form})

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        login = cleaned_data.get('login')
    
        if email and UsuarioNucleo.objects.filter(email=email).exists():
            raise forms.ValidationError({'email': 'Este correo electrónico ya está registrado.'})
    
        if login and UsuarioNucleo.objects.filter(login=login).exists():
            raise forms.ValidationError({'login': 'Este nombre de usuario ya está en uso.'})
    
        return cleaned_data


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember = form.cleaned_data.get('remember', False)
            
            try:
                usuario = UsuarioNucleo.objects.get(login=username)
                #if usuario.check_password(password) and usuario.activo:
                if check_password(password, usuario.password) and usuario.activo:
                    #from django.contrib.auth import login  
                    #login(request, usuario)  #NO funciona bien : El error ocurre porque se llama a login(request, usuario), 
                    #Django internamente intenta actualizar last_login y otros campos que el modelo estándar de Django tiene, 
                    #pero el modelo UsuarioNucleo no tiene esos campos.
                    
                    # Gestionar sesión manualmente
                    from django.contrib.sessions.models import Session
                    from django.contrib.auth import get_user_model
                    
                    # Guardar en sesión
                    request.session['usuario_id'] = usuario.pk
                    request.session['usuario_login'] = usuario.login
                    request.session['usuario_nivel'] = usuario.nivel_acceso
                    
                    # Recordarme: sesión duradera
                    if not remember:
                        request.session.set_expiry(0)
                    
                    return redirect('dashboard')
                else:
                    form.add_error(None, 'Usuario o contraseña incorrectos')
            except UsuarioNucleo.DoesNotExist:
                form.add_error(None, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    
    return render(request, 'registration/login.html', {'form': form})
    
def logout_view(request):
    """Cierra la sesión del usuario."""
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')
    
def lista_usuarios(request):
    """Lista todos los usuarios del nucleo."""
    
    # 1. Obtiene el parámetro 'view' de la URL (ej: ?view=grid)
    # Si no existe, usa 'list' por defecto
    vista = request.GET.get('view', 'list')
    
    # 2. Obtiene todos los usuarios de la base de datos
    usuarios = UsuarioNucleo.objects.all()
    
    # 3. Calcula totales y contadores
    total = usuarios.count()
    activos = usuarios.filter(activo=True).count()
    inactivos = total - activos
    
    # 4. Cuenta usuarios por nivel de acceso
    nivel_basico = usuarios.filter(nivel_acceso=1).count()
    nivel_avanzado = usuarios.filter(nivel_acceso=2).count()
    nivel_admin = usuarios.filter(nivel_acceso=3).count()
    
    # 5. Renderiza la plantilla con todos los datos
    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,  # Lista completa para mostrar en tabla
        'vista': vista,   # Para cambiar entre vista lista/grid
        'total': total,
        'activos': activos,
        'inactivos': inactivos,
        'nivel_basico': nivel_basico,
        'nivel_avanzado': nivel_avanzado,
        'nivel_admin': nivel_admin,
    })


def crear_usuario(request):
    """Crea un nuevo usuario del nucleo."""
    
    
    # Verificacion de nivel de acceso
    if request.session.get('usuario_nivel', 0) != 2:
            messages.error(request, 'Solo los administradores pueden crear usuarios.')
            return redirect('usuarios:lista')
    
    
    
    
    # 1. Verifica si se envio el formulario (POST) o se accede por primera vez (GET)
    if request.method == 'POST':
        
        # 2. Recibe los datos del formulario
        form = UsuarioNucleoForm(request.POST)
        
        if form.is_valid():
            # Verificar email duplicado antes de guardar
            email = form.cleaned_data.get('email')
            login = form.cleaned_data.get('login')
    
            if UsuarioNucleo.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está registrado.')
                return render(request, 'usuarios/crear.html', {'form': form})
    
            if UsuarioNucleo.objects.filter(login=login).exists():
                form.add_error('login', 'Este nombre de usuario ya está en uso.')
                return render(request, 'usuarios/crear.html', {'form': form})
            
            
            
            # 4. Guarda en memoria pero no en BD todavia
            usuario = form.save(commit=False)
            
             # 5. Procesa la contraseña
            password = form.cleaned_data.get('nueva_password')
            if password:
                usuario.password = make_password(password)  # Hashea la contraseña
            else:
                # El form ya valida en clean_nueva_password que es obligatorio para nuevos usuarios
                # pero por seguridad dejar un default o dejar que falle la validación
                usuario.password = make_password('changeme123')  # Default si no puso nada
            
            # 6. Guarda finalmente en la base de datos            
            usuario.save()
            
            # 7. Mensaje de éxito y redirección
            messages.success(request, f'Usuario {usuario.nombre} creado correctamente.')
            
            return redirect('usuarios:lista')
            
    # Si es GET (primera vez que entra), muestra el formulario vacío
    else:
        form = UsuarioNucleoForm()
    
    # Renderiza la plantilla con el formulario
    return render(request, 'usuarios/crear.html', {
        'form': form
    })


def editar_usuario(request, pk):
    """Edita un usuario existente."""    
    
    #Verificacion de acceso
    # Obtener el usuario que hace la petición desde la sesión
    #usuario_id = request.session.get('usuario_id')
    #nivel_actual = request.session.get('usuario_nivel', 0)
    
    # Solo administradores (nivel 2) pueden editar
    if request.session.get('usuario_nivel', 0) != 2:
        messages.error(request, 'Solo los administradores pueden editar usuarios.')
        return redirect('usuarios:lista')
        
        
        
    
    # 1. Obtiene el usuario por su PK (id). Si no existe, devuelve 404
    usuario = get_object_or_404(UsuarioNucleo, pk=pk)
    
    
    if request.method == 'POST':
        # 2. Instancia el formulario con los datos del usuario existente (instance=usuario)
        # Esto metera en los campos los valores actuales
        form = UsuarioNucleoForm(request.POST, instance=usuario)
        
        if form.is_valid():
            # Verificar email/login duplicados (excluyendo el propio usuario)
            email = form.cleaned_data.get('email')
            login = form.cleaned_data.get('login')
            if UsuarioNucleo.objects.filter(email=email).exclude(pk=pk).exists():
                form.add_error('email', 'Este correo electrónico ya está registrado.')
                return render(request, 'usuarios/editar.html', {'form': form, 'usuario': usuario})
            if UsuarioNucleo.objects.filter(login=login).exclude(pk=pk).exists():
                form.add_error('login', 'Este nombre de usuario ya está en uso.')
                return render(request, 'usuarios/editar.html', {'form': form, 'usuario': usuario})
            
            # GUARDAR password original ANTES de save(commit=False)
            #password_original = usuario.password
            
            # 3. Guarda en memoria sin commit
            usuario = form.save(commit=False)
            
            # 4. Solo actualiza password si se proporcionó una nueva
            #password = form.cleaned_data.get('password')  
            
            # Usar el nuevo campo 'nueva_password'
            nueva_password = form.cleaned_data.get('nueva_password')
            if nueva_password:
                usuario.password = make_password(nueva_password)
                
            # Si está vacío, NO tocamos el password actual
            '''
            if password:
                usuario.password = make_password(password)
            else:
                # Restaurar password original si está vacío
                usuario.password = password_original
            '''
            
            # 5. Guarda los cambios en BD
            usuario.save()
            
            messages.success(request, f'Usuario {usuario.nombre} actualizado correctamente.')
            
            return redirect('usuarios:lista')
    else:
        # 6. GET: Formulario con los datos actuales del usuario
        form = UsuarioNucleoForm(instance=usuario)
    
    return render(request, 'usuarios/editar.html', {
        'form': form,
        'usuario': usuario
    })


def eliminar_usuario(request, pk):
    """Elimina un usuario."""
    
    # Verificacion de nivel de acceso
    if request.session.get('usuario_nivel', 0) != 2:
            messages.error(request, 'Solo los administradores pueden eliminar usuarios.')
            return redirect('usuarios:lista')
    
    # 1. Obtiene el usuario a eliminar
    usuario = get_object_or_404(UsuarioNucleo, pk=pk)
    
    # 2. Guarda el nombre antes de eliminar (para mostrar en el mensaje)
    nombre = usuario.nombre
    
    # 3. Elimina el registro de la base de datos
    if request.session.get('usuario_nivel', 0) == 2:
        usuario.delete()
    
    # 4. Mensaje de éxito y redirección
    
    messages.success(request, f'Usuario {nombre} eliminado correctamente.')
    return redirect('usuarios:lista')
    
    
