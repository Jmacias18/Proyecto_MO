from django import forms
from django.forms.widgets import TimeInput
from .models import ParosProduccion, Procesos, Maquinaria, Conceptos, Clientes, Productos

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

    ID_Cliente = forms.ModelChoiceField(queryset=Clientes.objects.all(), required=True)
    ID_Producto = forms.CharField(required=True)  # Cambiar a CharField para aceptar cualquier valor

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs['instance']
            self.fields['ID_Producto'].initial = instance.ID_Producto
        elif 'data' in kwargs:
            data = kwargs['data']
            if 'ID_Cliente' in data:
                self.fields['ID_Producto'].initial = data.get('ID_Producto')

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
            'HoraInicio': forms.TimeInput(attrs={'type': 'time'}),
            'HoraFin': forms.TimeInput(attrs={'type': 'time'}),
        }

class ProcesosForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ['Nombre_Pro']

class MaquinariaForm(forms.ModelForm):
    class Meta:
        model = Maquinaria
        fields = ['ID_Maquinaria', 'DescripcionMaq', 'AreaMaq']
        
class ConceptosForm(forms.ModelForm):
    class Meta:
        model = Conceptos
        fields = ['ID_Concepto', 'Desc_Concepto']



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