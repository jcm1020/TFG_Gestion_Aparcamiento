from django.urls import path
from . import views

app_name = 'espacios'

urlpatterns = [
    path('', views.lista_espacios, name='lista'),
    path('crear/', views.crear_espacio, name='crear'),
    path('editar/<int:pk>/', views.editar_espacio, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_espacio, name='eliminar'),
]