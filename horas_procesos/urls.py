from django.urls import path
from .views import gestion_horas_procesos, actualizar_horas_procesos, sync_to_server_view

app_name = 'horas_procesos'

urlpatterns = [
    path('gestion_horas_procesos/', gestion_horas_procesos, name='gestion_horas_procesos'),
    path('actualizar_horas_procesos/', actualizar_horas_procesos, name='actualizar_horas_procesos'),
    path('sync-to-server/', sync_to_server_view, name='sync_to_server'),
]