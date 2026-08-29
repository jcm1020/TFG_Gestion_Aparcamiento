from django.urls import path
from . import views


app_name = 'usuarios'  # define el namespace


urlpatterns = [
    # Ruta principal - Página de Inicio / Home
    path('', views.index, name='index'),
    
    # Página de Login
    path('login/', views.login_view, name='login'),

    # Página de Registro  
    path('registro/', views.registro_view, name='registro'),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),   # 🔥ruta para cerrar sesión

    # CRUD Usuarios (F1)
    path('lista/', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar'),
]