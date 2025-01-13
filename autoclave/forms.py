from django import forms
from .models import Refrigerador
from .models import AutoclaveTemperature

class AutoclaveTemperatureForm(forms.ModelForm):
    id_refrigerador = forms.ChoiceField()  # Cargar dinámicamente los refrigeradores

    class Meta:
        model = AutoclaveTemperature
        fields = ['fecha', 'hora', 'temp_c', 'temp_termometro_c', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Asegúrate de que 'observaciones' esté vacío si es None
        if self.instance and self.instance.observaciones is None:
            self.instance.observaciones = ''
            self.fields['observaciones'].initial = ''
        # Cargar los refrigeradores desde la base de datos 'spf_info' usando 'using'
        try:
            refrigeradores = Refrigerador.objects.using('spf_info').filter(estado=True, sync=True)
            self.fields['id_refrigerador'].choices = [(r.id_refrigerador, r.descripcion_ref) for r in refrigeradores]
        except Exception as e:
            print(f"Error al cargar refrigeradores desde spf_info: {e}")
            self.fields['id_refrigerador'].choices = []

    def clean_id_refrigerador(self):
        id_refrigerador = self.cleaned_data.get('id_refrigerador')
        if not id_refrigerador:
            raise forms.ValidationError("Debe seleccionar un refrigerador.")
        return id_refrigerador

    def clean_temp_c(self):
        temp_c = self.cleaned_data.get('temp_c')
        if temp_c < 0 or temp_c > 150:
            raise forms.ValidationError("La temperatura en grados Celsius debe estar entre 0 y 150.")
        return temp_c

    def clean_temp_termometro_c(self):
        temp_termometro_c = self.cleaned_data.get('temp_termometro_c')
        if temp_termometro_c < 0 or temp_termometro_c > 150:
            raise forms.ValidationError("La temperatura del termómetro debe estar entre 0 y 150.")
        return temp_termometro_c
