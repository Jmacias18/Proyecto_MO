from django.db import models
from procesos.models import Empleados

class Horasprocesos(models.Model):
    id_hrspro = models.AutoField(db_column='ID_HrsProcesos', primary_key=True)
    fecha_hrspro = models.DateField(db_column='Fecha_HrsProcesos')
    codigo_emp = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Codigo_Emp', related_name='horasprocesos_horas')
    ID_Asis = models.CharField(db_column='ID_Asis', max_length=3, null=True, blank=True)  # Ajustar para almacenar el ID del tipo de inasistencia como cadena de texto
    id_pro = models.IntegerField(db_column='ID_Proceso', null=True, blank=True)
    horaentrada = models.TimeField(db_column='HoraEntrada', null=True, blank=True)
    horasalida = models.TimeField(db_column='HoraSalida', null=True, blank=True)
    hrs = models.FloatField(db_column='Hrs', null=True, blank=True)
    totalhrs = models.FloatField(db_column='TotalHrs', null=True, blank=True)
    hrsextras = models.FloatField(db_column='HrsExtras', null=True, blank=True)
    id_producto = models.CharField(max_length=10, null=True, blank=True)  # Ajustar a CharField
    autorizado = models.BooleanField(db_column='Autorizado')
    sync = models.BooleanField(db_column='SYNC')
    ucreado = models.CharField(db_column='UCreado', max_length=20, null=True, blank=True)  # Nueva columna UCreado
    umod = models.CharField(db_column='UMod', max_length=20, null=True, blank=True)  # Nueva columna UMod
    fmod = models.DateField(db_column='FMod', null=True)  # Nueva columna FMod
    hrcomida = models.BooleanField(default=False)  # Asegúrate de que este campo esté definido
    class Meta:
        db_table = 'HorasProcesos'
        managed = True


class Motivo(models.Model):
    codigo_emp = models.CharField(max_length=10)
    nombre_emp = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    motivo = models.TextField(max_length=350)
    sync = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Motivo'  # Especifica el nombre de la tabla en la base de datos

    def __str__(self):
        return f'{self.codigo_emp} - {self.motivo}'