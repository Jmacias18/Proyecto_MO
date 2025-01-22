from django.urls import path
from .views import AutoclaveTemperatureListView, AutoclaveTemperatureCreateView, sync_data_view, temperature_delete, temperature_edit, update_verification, AutoclaveCreateView

app_name = 'autoclave'

urlpatterns = [
    path('', AutoclaveTemperatureListView.as_view(), name='temperature_list'),  # Listado de temperaturas
    path('add/', AutoclaveTemperatureCreateView.as_view(), name='temperature_add'),  # Formulario para agregar temperatura
    path('edit/<int:id_temp_autoclave>/', temperature_edit, name='temperature_edit'),  # Modificar temperatura
    path('delete/<int:id_temp_autoclave>/', temperature_delete, name='temperature_delete'),  # Eliminar temperatura
    path('sync/', sync_data_view, name='sync_data'),
    path('update_verification/', update_verification, name='update_verification'),
    path('add_autoclave/', AutoclaveCreateView.as_view(), name='add_autoclave'),  # Formulario para agregar autoclave
    
]