from django.urls import path
from . import views

urlpatterns = [
    # Ruta principal - Página de Inicio / Home
    path('', views.index, name='index'),
    
    # Página de Login
    path('login/', views.login, name='login'),

    # Página de Registro  
    path('registro/', views.registro, name='registro'),
]