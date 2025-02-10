# horas_procesos/forms.py
from django import forms
from procesos.models import Empleados, Procesos
from .models import Motivo

class HorasProcesosForm(forms.Form):
    empleado = forms.ModelChoiceField(queryset=Empleados.objects.all(), label="Empleado")
    proceso1 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 1")
    proceso2 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 2")
    proceso3 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 3")
    proceso4 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 4")
    proceso4 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 5")
    proceso4 = forms.ModelChoiceField(queryset=Procesos.objects.all(), label="Proceso 6")
    horas_extras = forms.IntegerField(label="Horas Extras")
    total = forms.IntegerField(label="Total")

class MotivoForm(forms.ModelForm):
    class Meta:
        model = Motivo
        fields = ['motivo']