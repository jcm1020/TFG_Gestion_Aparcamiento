from django.shortcuts import render

from .models import Usuarios
from .forms import UsuariosForm


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
Vistas para la app Usuarios (F1 - Gestion de Usuarios del Nucleo)
"""

def registro_view(request):
    """Vista para registro de nuevos usuarios."""
    if request.method == 'POST':
        
    else:
        

    return render(request, 'login/registro.html', {'form': form})

def login_view(request):
    """Vista de inicio de sesion con sesion manual."""
    if request.method == 'POST':
        
    else:
        

    return render(request, 'login/login.html', {'form': form})

def logout_view(request):
    """Cierra la sesion del usuario."""
    request.session.flush()
    return redirect('login')

def lista_usuarios(request):
    """Lista todos los usuarios del nucleo."""    

def crear_usuario(request):
    """Crea un nuevo usuario del nucleo (solo administradores)."""

def editar_usuario(request, pk):
    """Edita un usuario existente (solo administradores)."""

def eliminar_usuario(request, pk):
    """Elimina un usuario (solo administradores)."""    


