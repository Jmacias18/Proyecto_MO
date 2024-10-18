# procesos/urls.py
from django.urls import path
from .views import ProcesosListView, ProcesosCreateView, ProcesosUpdateView, activar_desactivar_proceso

app_name = 'procesos'

urlpatterns = [
    path('', ProcesosListView.as_view(), name='procesos_list'),
    path('add/', ProcesosCreateView.as_view(), name='procesos_add'),
    path('<int:pk>/edit/', ProcesosUpdateView.as_view(), name='procesos_edit'),
    path('<int:pk>/activar_desactivar/', activar_desactivar_proceso, name='procesos_activar_desactivar'),
]