from django.db import models

class Empleados(models.Model):
    codigo_emp = models.CharField(db_column='Codigo_Emp', max_length=50, primary_key=True)
    nombre_emp = models.CharField(db_column='Nombre_Emp', max_length=100)
    depto_emp = models.CharField(db_column='Depto_Emp', max_length=60)
    puesto_emp = models.CharField(db_column='Puesto_Emp', max_length=100)
    tipo_puesto = models.CharField(db_column='Tipo_Puesto', max_length=50)
    turno_emp = models.CharField(db_column='Turno_Emp', max_length=30, null=True, blank=True)
    supervisor = models.CharField(db_column='Supervisor', max_length=6, null=True, blank=True)

    def __str__(self):
        return self.nombre_emp

    class Meta:
        db_table = 'Empleados'


class Procesos(models.Model):
    id_pro = models.AutoField(db_column='ID_Pro', primary_key=True)
    nombre_pro = models.CharField(db_column='Nombre_Pro', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    estado_pro = models.BooleanField(db_column='Estado_Pro', default=True)

    class Meta:
        db_table = 'Procesos'