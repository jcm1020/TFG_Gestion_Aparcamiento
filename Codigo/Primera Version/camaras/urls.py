"""
URLs para la app Camaras (F2)
"""
from django.urls import path
from . import views

app_name = 'camaras'

urlpatterns = [
    path('', views.lista_camaras, name='lista'),
    path('crear/', views.crear_camara, name='crear'),
    path('editar/<int:pk>/', views.editar_camara, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_camara, name='eliminar'),
    path('capturar/<int:pk>/', views.toggle_captura, name='capturar'),
]
