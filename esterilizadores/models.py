from django.db import models
from production.models import Maquinaria

class TempEsterilizadores(models.Model):
    ID_TempEsterilizador = models.AutoField(primary_key=True)
    Fecha = models.DateField() 
    Hora = models.TimeField()   
    ID_Maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE, db_column='ID_Maquinaria', null=True)
    TempC = models.FloatField()
    TempF = models.FloatField()
    ACorrectiva = models.CharField(max_length=300, blank=True, null=True)
    APreventiva = models.CharField(max_length=300, blank=True, null=True)
    Observaciones = models.CharField(max_length=300, blank=True, null=True)
    Inspecciono = models.IntegerField(db_column='Inspecciono')
    Verifico = models.IntegerField(db_column='Verifico')
    SYNC = models.BooleanField(default=False)

    class Meta:
        db_table = 'TemperaturaEsterilizadores'
        managed = True  # Para no gestionar migraciones, ya existe en la base de datos
        app_label = 'esterilizadores'
        verbose_name = 'Temperatura Esterilizador'
        verbose_name_plural = 'Temperatura Esterilizadores'  # Nombre plural

    def __str__(self):
        return f"{self.ID_Maquinaria.DescripcionMaq} - {self.Fecha} {self.Hora}"
