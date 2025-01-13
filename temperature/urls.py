from django.urls import path
from .views import temperature_control_view, register_temp_view, edit_temp_view, delete_temp_view, sync_data_view, sync_refrigeradores_view

app_name = 'temperature'

urlpatterns = [
    path('', temperature_control_view, name='temperature'),  # Ruta principal para el control de temperatura
    path('register/', register_temp_view, name='register_temp'),  # Ruta para registrar temperatura
    path('control/', temperature_control_view, name='control'), 
    path('edit/<int:temp_id>/', edit_temp_view, name='edit_temp'),  # Ruta para editar un registro de temperatura
    path('delete/<int:temp_id>/', delete_temp_view, name='delete_temp'),  # Ruta para eliminar un registro de temperatura
    path('sync/', sync_data_view, name='sync_data'),  # Nueva ruta para la sincronización
    path('sync_refrigeradores/', sync_refrigeradores_view, name='sync_refrigeradores'),  # Nueva ruta para sincronizar refrigeradores
]
