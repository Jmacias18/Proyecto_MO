# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Empleados(models.Model):
    codigo_emp = models.CharField(db_column='Codigo_Emp', primary_key=True, max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    nombre_emp = models.CharField(db_column='Nombre_Emp', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    depto_emp = models.CharField(db_column='Depto_Emp', max_length=60, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    puesto_emp = models.CharField(db_column='Puesto_Emp', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    tipo_puesto = models.CharField(db_column='Tipo_Puesto', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    turno_emp = models.CharField(db_column='Turno_emp', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    supervisor = models.CharField(db_column='Supervisor', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Empleados'



class Horasprocesos(models.Model):
    id_hrspro = models.IntegerField(db_column='ID_HrsPro', primary_key=True)  # Field name made lowercase.
    codigo_emp = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Codigo_Emp')  # Field name made lowercase.
    id_pro = models.IntegerField(db_column='ID_Pro')  # Field name made lowercase.
    autorizado = models.BooleanField(db_column='Autorizado')  # Field name made lowercase.
    hrs = models.FloatField(db_column='Hrs')  # Field name made lowercase.
    fecha_hrspro = models.CharField(db_column='Fecha_HrsPro', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    horaentrada = models.TimeField(db_column='HoraEntrada')  # Field name made lowercase.
    horasalida = models.TimeField(db_column='HoraSalida')  # Field name made lowercase.
    totalhrs = models.FloatField(db_column='TotalHrs')  # Field name made lowercase.
    hrs= models.FloatField(db_column='Hrs')  # Field name made lowercase.
    hrsextras = models.FloatField(db_column='HrsExtras')  # Field name made lowercase.
    asistencia = models.BooleanField(db_column='Asistencia')  # Field name made lowercase.
    sync = models.BooleanField(db_column='SYNC')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'HorasProcesos'

class Procesos(models.Model):
    id_pro = models.IntegerField(db_column='ID_Pro', primary_key=True)  # Field name made lowercase.
    nombre_pro = models.CharField(db_column='Nombre_Pro', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    estado_pro = models.BooleanField(db_column='Estado_Pro', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Procesos'
