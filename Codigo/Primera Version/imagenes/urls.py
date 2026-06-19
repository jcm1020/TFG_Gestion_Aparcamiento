"""
URLs para la app Imagenes (F3)
"""
from django.urls import path
from . import views

app_name = 'imagenes'

urlpatterns = [
    path('', views.lista_imagenes, name='lista'),
    path('subir/', views.subir_imagen, name='subir'),
    path('eliminar/<int:pk>/', views.eliminar_imagen, name='eliminar'),
    path('marcar-referencia/<int:pk>/', views.marcar_referencia, name='marcar_referencia'),
    path('eliminar-todas/', views.eliminar_todas, name='eliminar_todas'),
]
