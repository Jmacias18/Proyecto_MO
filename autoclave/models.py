from django.db import models
from django.utils import timezone
from usuarios.models import CustomUser

class Maquinaria(models.Model):
    id_maquinaria = models.AutoField(primary_key=True, db_column='ID_Maquinaria')
    descripcion = models.CharField(max_length=150, db_column='DescripcionMaq')
    area = models.CharField(max_length=50, db_column='AreaMaq')
    sync = models.BooleanField(default=False, db_column='SYNC')
    estado = models.BooleanField(db_column='Estado')

    def __str__(self):
        return self.descripcion

    class Meta:
        db_table = 'Maquinaria'

class AutoclaveTemperature(models.Model):
    id_temp_autoclave = models.AutoField(primary_key=True, db_column='ID_TempAutoclave')
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)
    
    # Relación con Maquinaria usando ForeignKey
    id_maquinaria = models.ForeignKey(
        'Maquinaria',
        on_delete=models.CASCADE,
        db_column='ID_Maquinaria'
    )

    temp_c = models.FloatField(db_column='TempC')
    temp_f = models.FloatField(db_column='TempF')
    temp_termometro_c = models.FloatField(db_column='TempTermometroC')
    temp_termometro_f = models.FloatField(db_column='TempTermometroF')
    observaciones = models.TextField(blank=True, null=True, db_column='Observaciones')
    
    # Cambiar inspecciono y verificacion a IntegerField
    inspecciono = models.IntegerField(db_column='Inspecciono', blank=True, null=True)
    verificacion = models.IntegerField(db_column='Verificacion', blank=True, null=True)
    sync = models.BooleanField(default=False, db_column='SYNC')

    def __str__(self):
        return f"Temperatura {self.temp_c}°C - Maquinaria {self.id_maquinaria.descripcion}"

    class Meta:
        verbose_name = "Temperatura de Autoclave"
        verbose_name_plural = "Temperaturas de Autoclave"
        ordering = ['-fecha', '-hora']
        db_table = 'TemperaturaAutoclaves'