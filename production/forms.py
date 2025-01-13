from django import forms
from django.forms.widgets import TimeInput
from .models import ParosProduccion, Procesos, Maquinaria

class ParosProduccionForm(forms.ModelForm):
    class Meta:
        model = ParosProduccion
        fields = [
            'ID_Cliente',
            'OrdenFabricacionSAP',
            'ID_Producto',
            'HoraInicio',
            'HoraFin',
            'TiempoMuerto',
            'PersonasAfectadas',
            'MO',
            'ID_Proceso',
            'ID_Maquinaria',
            'Causa',
        ]
        widgets = {
            'HoraInicio': TimeInput(attrs={'type': 'time'}),
            'HoraFin': TimeInput(attrs={'type': 'time'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        HoraInicio = cleaned_data.get("HoraInicio")
        HoraFin = cleaned_data.get("HoraFin")

        if HoraInicio and HoraFin and HoraFin <= HoraInicio:
            raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
        
class ProcesosForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ['Nombre_Proc']

class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = ['DescripcionMaq', 'AreaMaq']

class ParoMantForm(forms.ModelForm):
    class Meta:
        model = ParosProduccion
        fields = ['Diagnostico', 'CausaRaiz']  # Solo los campos que deseas modificar


""" 
# Formulario para registrar un proceso
class ProcesosForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['Nombre_Proc']

# Formulario para registrar una maquinaria
class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = ['DescripcionMaq']

# Formulario para modificar un paro
class ParosModifyForm(ParosForm):
    def __init__(self, *args, **kwargs):
        super(ParosModifyForm, self).__init__(*args, **kwargs)
        # Puedes añadir lógica adicional aquí si es necesario

    # Aquí puedes agregar validaciones específicas para la modificación si es necesario
 """