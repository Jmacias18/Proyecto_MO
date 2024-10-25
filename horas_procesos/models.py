from django.db import models
from procesos.models import Empleados

class Horasprocesos(models.Model):
    id_hrspro = models.AutoField(db_column='ID_HrsProcesos', primary_key=True)
    fecha_hrspro = models.DateField(db_column='Fecha_HrsProcesos')
    codigo_emp = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Codigo_Emp', related_name='horasprocesos_horas')
    asistencia = models.BooleanField(db_column='Asistencia')
    id_pro = models.IntegerField(db_column='ID_Proceso', null=True, blank=True)
    horaentrada = models.TimeField(db_column='HoraEntrada', null=True, blank=True)
    horasalida = models.TimeField(db_column='HoraSalida', null=True, blank=True)
    hrs = models.FloatField(db_column='Hrs', null=True, blank=True)
    totalhrs = models.FloatField(db_column='TotalHrs', null=True, blank=True)
    hrsextras = models.FloatField(db_column='HrsExtras', null=True, blank=True)
    autorizado = models.BooleanField(db_column='Autorizado')
    sync = models.BooleanField(db_column='SYNC')

    class Meta:
        db_table = 'HorasProcesos'