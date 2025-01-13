from django.db import models

class Refrigerador(models.Model):
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
        app_label = 'esterilizadores'
        verbose_name = 'Refrigerador'
        verbose_name_plural = 'Refrigeradores'

    def __str__(self):
        return self.DescripcionRef
    
class TempEsterilizadores(models.Model):
    ID_TempEsterilizador = models.AutoField(primary_key=True)
    Fecha = models.DateField() 
    Hora = models.TimeField()   
    ID_Refrigerador = models.ForeignKey(Refrigerador, on_delete=models.CASCADE, db_column='ID_Refrigerador', null=True)
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
        return f"{self.ID_Refrigerador.DescripcionRef} - {self.Fecha} {self.Hora}"
