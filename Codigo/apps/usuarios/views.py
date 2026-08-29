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


