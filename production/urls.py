from django.urls import path
from . import views
app_name = 'production'  # Asegúrate de tener esto si usas un namespace

urlpatterns = [
    path('registrar_paro/', views.registrar_paro, name='registrar_paro'),
    path('production/', views.production, name='production'),
    path('registro/', views.registro, name='registro'),
    path('modificar_paro/<int:paro_id>/', views.modificar_paro, name='modificar_paro'),
    path('eliminar_paro/<int:paro_id>/', views.eliminar_paro, name='eliminar_paro'),
    path('registro_maquinaria/', views.registro_maquinaria, name='registro_maquinaria'),
    path('registro_proceso/', views.registro_proceso, name='registro_proceso'),
    path('registro_concepto/', views.registro_concepto, name='registro_concepto'),  # Nueva ruta para registrar concepto
    path('modificar_proceso/<int:proceso_id>/', views.modificar_proceso, name='modificar_proceso'),
    path('modificar_maquinaria/<int:maquinaria_id>/', views.modificar_maquinaria, name='modificar_maquinaria'),
    path('modificar_concepto/<int:concepto_id>/', views.modificar_concepto, name='modificar_concepto'),  # Nueva ruta para modificar concepto
    path('cambiar/estado/proceso/<int:id_proceso>/', views.cambiar_estado_proceso, name='cambiar_estado_proceso'),  # Cambiar estado de proceso
    path('cambiar/estado/maquinaria/<int:id_maquinaria>/', views.cambiar_estado_maquinaria, name='cambiar_estado_maquinaria'),  # Cambiar estado de maquinaria
    path('sync/', views.sync_data_view, name='sync_data_view'),  # Nueva ruta
    path('syncProc/', views.sync_procesos_view, name='sync_procesos'),  # Nueva ruta
    path('syncMaq/', views.sync_maquinaria_view, name='sync_maquinaria'),  # Nueva ruta 
    path('syncConceptos/', views.sync_conceptos_view, name='sync_conceptos'),  # Nueva ruta para sincronizar conceptos
    path('modificar_paro_mant/<int:paro_id>/', views.modificar_paro_mant, name='modificar_paro_mant'),
    path('filtrar_paros/', views.filtrar_paros, name='filtrar_paros'),
    path('get_productos/', views.get_productos, name='get_productos'),
]
