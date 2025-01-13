from django.db import models
from django.utils import timezone
from usuarios.models import CustomUser

class Refrigerador(models.Model):
    # Definimos los campos del modelo con los nombres correctos según la base de datos
    id_refrigerador = models.AutoField(primary_key=True, db_column='ID_Refrigerador')  # Aquí se asigna el nombre de columna correcto
    descripcion_ref = models.CharField(max_length=150, db_column='DescripcionRef')  # Asignamos el nombre correcto de columna
    min_temp = models.FloatField(db_column='Min')  # Aseguramos que la columna se llama 'Min' en la base de datos
    max_temp = models.FloatField(db_column='Max')  # Lo mismo para 'Max'
    tipo_refrigerador = models.CharField(max_length=50, db_column='TipoRefrigerador')  # 'TipoRefrigerador' en la base de datos
    sync = models.BooleanField(default=False, db_column='SYNC')
    estado = models.BooleanField(db_column='estado')  # La columna es 'estado'

    def __str__(self):
        return self.descripcion_ref

    class Meta:
        db_table = 'Refrigeradores'  # Nombre correcto de la tabla en la base de datos


class AutoclaveTemperature(models.Model):
    # 'id_temp_autoclave' como clave primaria autoincremental
    id_temp_autoclave = models.AutoField(primary_key=True, db_column='ID_TempAutoclave')

    # Fecha y hora de la medición
    fecha = models.DateField(default=timezone.now)
    hora = models.TimeField(default=timezone.now)

    # Relación con Refrigerador usando ForeignKey
    id_refrigerador = models.ForeignKey(
        'Refrigerador',  # Asegúrate de que el modelo Refrigerador esté correctamente importado
        on_delete=models.CASCADE,
        db_column='ID_Refrigerador'  # Especificamos el nombre de la columna en la base de datos
    )

    # Temperaturas en Celsius y Fahrenheit
    temp_c = models.FloatField(db_column='TempC')
    temp_f = models.FloatField(db_column='TempF')
    temp_termometro_c = models.FloatField(db_column='TempTermometroC')
    temp_termometro_f = models.FloatField(db_column='TempTermometroF')

    # Observaciones
    observaciones = models.TextField(blank=True, null=True, db_column='Observaciones')

    # Campos adicionales
    inspecciono = models.IntegerField(db_column='Inspecciono', blank=True)
    verificacion = models.IntegerField(null=True, blank=True, db_column='Verificacion')
    sync = models.BooleanField(default=False, db_column='SYNC')

    def __str__(self):
        return f"Temperatura {self.temp_c}°C - Refrigerador {self.id_refrigerador.descripcion_ref}"

    class Meta:
        verbose_name = "Temperatura de Autoclave"
        
        verbose_name_plural = "Temperaturas de Autoclave"
        ordering = ['-fecha', '-hora']
        db_table = 'TemperaturaAutoclaves'