"""
URLs para la app Zonas (F4)
"""
from django.urls import path
from . import views

app_name = 'zonas'

urlpatterns = [
    # Zonas
    path('', views.lista_zonas, name='lista'),
    path('registrar/', views.registrar_zona, name='registro'),
    path('editar/<int:pk>/', views.editar_zona, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_zona, name='eliminar_zona'),
    #Inicializar y reinicializar podrian ser asi
    #path('inicializar/', views.inicializar_sistema, name='inicializar'),
    #path('reinicializar/', views.reinicializar_sistema, name='reinicializar'),
    
    # Gestion DXF
    path('dxf/', views.lista_dxf, name='lista_dxf'),
    path('dxf/registrar/', views.registrar_dxf, name='registrar_dxf'),
    path('dxf/activar/<int:pk>/', views.activar_dxf, name='activar_dxf'),
    path('dxf/procesar/<int:pk>/', views.procesar_dxf, name='procesar_dxf'),
    path('dxf/eliminar/<int:pk>/', views.eliminar_dxf, name='eliminar_dxf'),
    path('dxf/debug/<int:pk>/', views.debug_dxf, name='debug_dxf'),
]