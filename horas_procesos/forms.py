# horas_procesos/forms.py
from django import forms
from procesos.models import Empleados, Procesos

class HorasProcesosForm(forms.Form):
    empleado = forms.ModelChoiceField(queryset=Empleados.objects.all(), label="Empleado")
    proceso1 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 1")
    proceso2 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 2")
    proceso3 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 3")
    proceso4 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 4")
    horas_extras = forms.IntegerField(label="Horas Extras")
    total = forms.IntegerField(label="Total")