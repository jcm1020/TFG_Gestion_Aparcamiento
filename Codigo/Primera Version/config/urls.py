"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
#Añadidos
from django.urls import include
from django.shortcuts import render
from usuarios.forms_auth import LoginForm
from django.contrib.auth import views as auth_views
from usuarios.views import registro_view, login_view, logout_view

def index_view(request):
    """Pagina de inicio publica."""
    return render(request, 'index.html')

def dashboard_view(request):
    """Dashboard principal del sistema."""
    from camaras.models import Camara
    from imagenes.models import Imagen
    from usuarios.models import UsuarioNucleo    

    
    # Contadores para el dashboard
    usuarios_count = UsuarioNucleo.objects.count()
    camaras_total = Camara.objects.count()
    camaras_online = Camara.objects.filter(estado='online').count()
    imagenes_count = Imagen.objects.count()
    

    
    return render(request, 'dashboard.html', {
        'usuarios_count': usuarios_count,
        'camaras_total': camaras_total,
        'camaras_online': camaras_online,
        'imagenes_count': imagenes_count,
        #'objetos_reconocidos': objetos_reconocidos,
        #'alertas_nuevas': alertas_nuevas,
        #'alertas_criticas': alertas_criticas,
        #'reglas_activas': reglas_activas,
        #'plazas_totales': plazas_totales,
        #'plazas_ocupadas': plazas_ocupadas,
        #'plazas_libres': plazas_libres,
        #'ocupacion': ocupacion,
        #'alertas_recientes': alertas_recientes,
        #'en_ejecucion': en_ejecucion
    })

urlpatterns = [
    # Administracion
    path('admin/', admin.site.urls),
    
    # Pagina de inicio
    path('', index_view, name='index'),
    
    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Autenticacion
    #path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', form_class=LoginForm), name='login'),
    path('login/', login_view, name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #Funciona correctamente porque solo destruye la sesión del usuario en Django (request.session.flush()), 
    #no necesita verificar contra ningún modelo de usuario.
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #Usamos uno personalizado
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registro'),
    #path('registro/', auth_views.TemplateView.as_view(template_name='registration/registro.html'), name='registro'),
    path('perfil/', auth_views.TemplateView.as_view(template_name='registration/perfil.html'), name='perfil'),
    
    
    # Apps
    path('usuarios/', include('usuarios.urls')),
    path('camaras/', include('camaras.urls')),
    path('imagenes/', include('imagenes.urls')),
    path('zonas/', include('zonas.urls')),
    
    
]
