from django.db import models
from procesos.models import Empleados

class Horasprocesos(models.Model):
    id_hrspro = models.AutoField(db_column='ID_HrsProcesos', primary_key=True)
    fecha_hrspro = models.DateField(db_column='Fecha_HrsProcesos')
    codigo_emp = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Codigo_Emp', related_name='horasprocesos_horas')
    asistencia = models.BooleanField(db_column='Asistencia')
    id_pro = models.IntegerField(db_column='ID_Proceso')
    horaentrada = models.TimeField(db_column='HoraEntrada')
    horasalida = models.TimeField(db_column='HoraSalida')
    hrs = models.FloatField(db_column='Hrs')
    totalhrs = models.FloatField(db_column='TotalHrs')
    hrsextras = models.FloatField(db_column='HrsExtras')
    autorizado = models.BooleanField(db_column='Autorizado', null=True, blank=True)
    sync = models.BooleanField(db_column='SYNC', null=True, blank=True)

    class Meta:
        db_table = 'HorasProcesos'