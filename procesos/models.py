# procesos/models.py
from django.db import models

class Empleados(models.Model):
    codigo_emp = models.CharField(db_column='Codigo_Emp', primary_key=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    nombre_emp = models.CharField(db_column='Nombre_Emp', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    depto_emp = models.CharField(db_column='Depto_Emp', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')
    puesto_emp = models.CharField(db_column='Puesto_Emp', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    tipo_puesto = models.CharField(db_column='Tipo_Puesto', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')
    turno_emp = models.CharField(db_column='Turno_emp', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    supervisor = models.CharField(db_column='Supervisor', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Empleados'


class Horasprocesos(models.Model):
    id_hrspro = models.IntegerField(db_column='ID_HrsPro', primary_key=True)
    codigo_emp = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Codigo_Emp')
    id_pro = models.IntegerField(db_column='ID_Pro')
    autorizado = models.BooleanField(db_column='Autorizado')
    hrs = models.FloatField(db_column='Hrs')
    fecha_hrspro = models.CharField(db_column='Fecha_HrsPro', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')

    class Meta:
        managed = False
        db_table = 'HorasProcesos'


class Procesos(models.Model):
    id_pro = models.AutoField(db_column='ID_Pro', primary_key=True)
    nombre_pro = models.CharField(db_column='Nombre_Pro', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    estado_pro = models.BooleanField(db_column='Estado_Pro', default=True)

    class Meta:
        db_table = 'Procesos'
