"""
URLs para la app Usuarios (F1)
"""
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.lista_usuarios, name='lista'),
    path('crear/', views.crear_usuario, name='crear'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar'),
]
