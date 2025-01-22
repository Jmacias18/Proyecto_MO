from django import forms
from .models import TempEsterilizadores

class TempEsterilizadoresForm(forms.ModelForm):
    Fecha = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
        input_formats=['%Y-%m-%d', '%m/%d/%Y']
    )
    Inspecciono = forms.ChoiceField(
        choices=[(1, 'Sí'), (0, 'No')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    Verifico = forms.ChoiceField(
        choices=[(1, 'Sí'), (0, 'No')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = TempEsterilizadores
        fields = ['Fecha', 'Hora', 'ID_Maquinaria', 'TempC', 'TempF', 'ACorrectiva', 'APreventiva', 'Observaciones', 'Inspecciono', 'Verifico']
        widgets = {
            'Fecha': forms.DateInput(attrs={'type': 'date'}),
            'Hora': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegúrate de que los campos Fecha y Hora sean obligatorios
        self.fields['Fecha'].required = True
        self.fields['Hora'].required = True
        # Otros campos pueden ser opcionales si es necesario
        self.fields['ID_Maquinaria'].required = True
        self.fields['TempC'].required = True
        self.fields['TempF'].required = True
        self.fields['ACorrectiva'].required = False
        self.fields['APreventiva'].required = False
        self.fields['Observaciones'].required = False