from django.urls import path
from .views import gestion_horas_procesos

app_name = 'horas_procesos'

urlpatterns = [
    path('gestion_horas_procesos/', gestion_horas_procesos, name='gestion_horas_procesos'),
]