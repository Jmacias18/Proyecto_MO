# forms.py
from django import forms
from .models import TempEsterilizadores

class TempEsterilizadoresForm(forms.ModelForm):
    class Meta:
        model = TempEsterilizadores
        fields = ['Fecha', 'Hora', 'ID_Refrigerador', 'TempC', 'TempF', 'ACorrectiva', 'APreventiva', 'Observaciones']
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
        self.fields['ID_Refrigerador'].required = True
        self.fields['TempC'].required = True
        self.fields['TempF'].required = True
        self.fields['ACorrectiva'].required = False
        self.fields['APreventiva'].required = False
        self.fields['Observaciones'].required = False