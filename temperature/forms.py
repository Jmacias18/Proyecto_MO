#forms.py
from django import forms
from .models import TemperaturaAreas, Refrigeradores

class TempAreaForm(forms.ModelForm):
    class Meta:
        model = TemperaturaAreas
        fields = ['Fecha', 'Hora', 'ID_Refrigerador', 'Temperatura', 'SYNC', 'Comentarios']

class RefrigeradoresForm(forms.ModelForm):
    class Meta:
        model = Refrigeradores
        fields = ['DescripcionRef', 'Min', 'Max', 'TipoRefrigerador', 'SYNC', 'estado']  # Agrega sync y estado

    def clean(self):
        cleaned_data = super().clean()
        min_temp = cleaned_data.get('Min')
        max_temp = cleaned_data.get('Max')

        if min_temp is not None and max_temp is not None and min_temp > max_temp:
            raise forms.ValidationError('El valor mínimo no puede ser mayor que el valor máximo.')

        return cleaned_data

