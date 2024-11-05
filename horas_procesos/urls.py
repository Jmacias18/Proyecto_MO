from django.urls import path
from .views import gestion_horas_procesos, sync_to_server_view,editar_registros,obtener_registros



app_name = 'horas_procesos'

urlpatterns = [
    path('gestion_horas_procesos/', gestion_horas_procesos, name='gestion_horas_procesos'),
    path('sync-to-server/', sync_to_server_view, name='sync_to_server'),
    path('editar_registros/',editar_registros, name='editar_registros'),
    path('obtener_registros/',obtener_registros, name='obtener_registros'),
]
