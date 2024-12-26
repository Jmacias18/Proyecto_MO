from django.db import models

from django.db import models

class Empleados(models.Model):
    codigo_emp = models.IntegerField(db_column='Codigo_Emp', primary_key=True)  # Field name and type updated.
    nombre_emp = models.CharField(db_column='Nombre_Emp', max_length=255)  # Field length updated.
    estado = models.CharField(db_column='Estado', max_length=1)  # New field added.
    id_departamento = models.IntegerField(db_column='ID_Departamento')  # New field added.
    id_puesto = models.IntegerField(db_column='ID_Puesto')  # New field added.
    id_turno = models.CharField(db_column='ID_Turno', max_length=10)  # New field added.
    id_supervisor = models.CharField(db_column='ID_Supervisor', max_length=10, blank=True, null=True)  # New field added.

    class Meta:
        managed = True
        db_table = 'Empleados'
    
    def __str__(self):
        return self.nombre_emp


class Procesos(models.Model):
    id_pro = models.AutoField(db_column='ID_Pro', primary_key=True)
    nombre_pro = models.CharField(db_column='Nombre_Pro', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')
    estado_pro = models.BooleanField(db_column='Estado_Pro', default=True)

    class Meta:
        db_table = 'Procesos'