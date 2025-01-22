from django import forms
from .models import AutoclaveTemperature, Maquinaria

class AutoclaveTemperatureForm(forms.ModelForm):
    id_maquinaria = forms.ChoiceField()  # Cargar dinámicamente las maquinarias

    class Meta:
        model = AutoclaveTemperature
        fields = ['fecha', 'hora', 'temp_c', 'temp_f', 'temp_termometro_c', 'temp_termometro_f', 'observaciones']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.observaciones is None:
            self.instance.observaciones = ''
            self.fields['observaciones'].initial = ''
        
        try:
            # Filtrar maquinarias que contienen "AutoClave #" en la descripción
            maquinarias = Maquinaria.objects.using('spf_info').filter(descripcion__icontains='AutoClave #')
            self.fields['id_maquinaria'].choices = [(m.id_maquinaria, m.descripcion) for m in maquinarias]
        except Exception as e:
            print(f"Error al cargar maquinarias desde spf_info: {e}")
            self.fields['id_maquinaria'].choices = []

        # Establecer el valor inicial del campo id_maquinaria
        if self.instance and self.instance.pk:
            self.fields['id_maquinaria'].initial = self.instance.id_maquinaria.id_maquinaria

    def clean_id_maquinaria(self):
        id_maquinaria = self.cleaned_data.get('id_maquinaria')
        if not id_maquinaria:
            raise forms.ValidationError("Debe seleccionar una maquinaria.")
        return id_maquinaria

    def clean_temp_c(self):
        temp_c = self.cleaned_data.get('temp_c')
        if temp_c < 0 or temp_c > 150:
            raise forms.ValidationError("La temperatura en grados Celsius debe estar entre 0 y 150.")
        return temp_c

    def clean_temp_termometro_c(self):
        temp_termometro_c = self.cleaned_data.get('temp_termometro_c')
        if temp_termometro_c < 0 or temp_termometro_c > 150:
            raise forms.ValidationError("La temperatura del termómetro en grados Celsius debe estar entre 0 y 150.")
        return temp_termometro_c