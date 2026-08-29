"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
#from apps.usuarios.views import registro_view, login_view, logout_view

# Python busca dashboard_view al evaluar las rutas, 
# pero como está definida arriba antes, existe, 
# si la ponemos más abajo en el mismo archivo, 
# no existe aún cuando se evalúa.
# Poner esto si se pone mas abajo:
'''
from . import views as local_views  # IMPORTAR EL MISMOMÓDULO
urlpatterns = [
    path('dashboard/', local_views.dashboard_view, name='dashboard'),  # USAR CON ALIAS
]
'''
def dashboard_view(request):
    """Dashboard principal del sistema."""
    from apps.usuarios.models import Usuarios

    usuarios_count = Usuarios.objects.count()
    usuarios_activos = Usuarios.objects.filter(activo=True).count()
    usuarios_inactivos = usuarios_count - usuarios_activos
    usuarios_admin = Usuarios.objects.filter(nivel_acceso=2).count()

    return render(request, 'dashboard.html', {
        'usuarios_count': usuarios_count,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'usuarios_admin': usuarios_admin,
    })

urlpatterns = [
    # Panel de administración Django
    path('admin/', admin.site.urls),
    # Aplicación usuarios - incluye todas las rutas de usuarios
    path('', include('apps.usuarios.urls', namespace='usuarios')),    
    # Ruta específica para el dashboard (si no se accede por navbar)
    path('dashboard/', dashboard_view, name='dashboard'),

]

# Servir archivos estáticos y media en desarrollo
'''if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    # Media files (archivos subidos por usuarios)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Static files (CSS, JavaScript, Images)
    urlpatterns += staticfiles_urlpatterns()'''

'''
def index_view(request):
    """Pagina de inicio publica."""
    return render(request, 'index.html')
'''


