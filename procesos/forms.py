
from django import forms
from .models import Procesos

class ProcesosForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ['nombre_pro', 'estado_pro']

    def clean_nombre_pro(self):
        nombre_pro = self.cleaned_data.get('nombre_pro')
        if Procesos.objects.filter(nombre_pro=nombre_pro).exists():
            raise forms.ValidationError("Ya existe un proceso con este nombre.")
        return nombre_pro