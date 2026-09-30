from django.urls import path

from . import views


app_name = 'espacios'


urlpatterns = [
    path('lista/', views.lista_espacios, name='lista'),
    path('localizacion/', views.editar_localizacion, name='localizacion'),
    path('crear/', views.crear_espacio, name='crear'),
    path('editar/<int:pk>/', views.editar_espacio, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_espacio, name='eliminar'),
]