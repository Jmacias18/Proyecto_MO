from django import forms
from django.forms.widgets import TimeInput
from .models import ParosProduccion, Procesos, Maquinaria, Conceptos

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
            'ID_Concepto',  # Añadir el campo ID_Concepto
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
        ID_Maquinaria = cleaned_data.get("ID_Maquinaria")
        ID_Concepto = cleaned_data.get("ID_Concepto")

        if HoraInicio and HoraFin and HoraFin <= HoraInicio:
            raise forms.ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

        if not ID_Maquinaria and not ID_Concepto:
            raise forms.ValidationError("Debe seleccionar Maquinaria o Concepto.")

        # Enviar vacío para ID_Concepto si se selecciona Maquinaria
        if ID_Concepto == '0' or ID_Concepto == 0:
            cleaned_data['ID_Concepto'] = None

        # Enviar vacío para Diagnostico, CausaRaiz y AccionesMantenimiento
        cleaned_data['Diagnostico'] = ''
        cleaned_data['CausaRaiz'] = ''
        cleaned_data['AccionesMantenimiento'] = ''

        return cleaned_data

class ParoMantForm(forms.ModelForm):
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
            'ID_Concepto',
            'Causa',
            'Diagnostico',
            'CausaRaiz',
            'AccionesMantenimiento',
        ]
        widgets = {
            'HoraInicio': TimeInput(attrs={'type': 'time'}),
            'HoraFin': TimeInput(attrs={'type': 'time'}),
        }

class ProcesosForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ['Nombre_Pro']

class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = ['DescripcionMaq', 'AreaMaq']


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