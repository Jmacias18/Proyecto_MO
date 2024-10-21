# horas_procesos/models.py
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