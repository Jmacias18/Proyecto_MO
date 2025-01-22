from django.urls import path
from . import views
app_name = 'esterilizadores'  # Asegúrate de tener esto si usas un namespace

urlpatterns = [
    path('tempester/', views.mostrar_datos, name='tempester'),
    path('registrotemp/', views.registrotemp, name='registrotemp'),
    path('sync/', views.sync_data_view, name='sync_data'),  
    path('modificar/<int:id>/', views.modificar_temp, name='modificar'),
    path('borrar/<int:id>/', views.borrar_temp, name='borrar'), 
]