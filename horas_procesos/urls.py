from django.urls import path
from .views import gestion_horas_procesos, actualizar_horas_procesos, sync_to_server_view, eliminar_proceso,actualizar_horas_procesos,eliminar_proceso,display_employees,agregar_motivo,eliminar_motivo,actualizar_motivo,empleados_por_departamento
app_name = 'horas_procesos'

urlpatterns = [
    path('gestion_horas_procesos/', gestion_horas_procesos, name='gestion_horas_procesos'),
    path('actualizar_horas_procesos/', actualizar_horas_procesos, name='actualizar_horas_procesos'),
    path('sync-to-server/', sync_to_server_view, name='sync_to_server'),
    path('eliminar_proceso/<int:id_hrspro>/', eliminar_proceso, name='eliminar_proceso'),
    path('eliminar_todos_procesos/', eliminar_proceso, name='eliminar_todos_procesos'),
    path('actualizar_proceso/<int:id_hrspro>/', actualizar_horas_procesos, name='actualizar_proceso'),
    path('display_employees/', display_employees, name='display_employees'),
    path('agregar_motivo/', agregar_motivo, name='agregar_motivo'),
    path('eliminar_motivo/<int:id>/', eliminar_motivo, name='eliminar_motivo'),
    path('actualizar_motivo/<int:id>/', actualizar_motivo, name='actualizar_motivo'),
    path('empleados_por_departamento/', empleados_por_departamento, name='empleados_por_departamento'),
    
]
    