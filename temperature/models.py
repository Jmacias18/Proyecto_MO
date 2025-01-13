from django.db import models

class Refrigeradores(models.Model):
    ID_Refrigerador = models.AutoField(primary_key=True)
    DescripcionRef = models.CharField(max_length=150)
    Min = models.FloatField(null=True)
    Max = models.FloatField(null=True)
    TipoRefrigerador = models.CharField(max_length=50, null=True)
    SYNC = models.BooleanField(default=False)  # Campo para sincronización
    estado = models.BooleanField(default=True)  # Campo para estado (True: activo, False: inactivo)

    class Meta:
        db_table = 'Refrigeradores'
        managed = True  # Para no gestionar migraciones, ya existe en la base de datos
        app_label = 'temperature'
        verbose_name = 'Refrigerador'
        verbose_name_plural = 'Refrigeradores'

    def __str__(self):
        return self.DescripcionRef



class TemperaturaAreas(models.Model):
    ID_TempAreas = models.AutoField(primary_key=True)
    Fecha = models.DateField()
    Hora = models.TimeField()
    ID_Refrigerador = models.ForeignKey(Refrigeradores, on_delete=models.SET_NULL, db_column='ID_Refrigerador',null=True)
    Temperatura = models.FloatField()
    Comentarios = models.TextField(blank=True, null=True)
    SYNC = models.BooleanField(default=False)

    class Meta:
        db_table = 'TemperaturaAreas'
        managed = True  # Para no gestionar migraciones, ya existe en la base de datos
        verbose_name = 'Temperatura Areas'
        verbose_name_plural = 'Temperatura Areas'  # Nombre plural
    def __str__(self):
        return f"{self.ID_Refrigerador.DescripcionRef} - {self.Fecha} {self.Hora}"
