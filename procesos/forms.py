# procesos/forms.py
from django import forms
from .models import Procesos

class ProcesosForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ['nombre_pro', 'estado_pro']
        