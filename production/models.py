from django.db import models

class Procesos(models.Model):
    ID_Proc = models.AutoField(primary_key=True)
    Nombre_Proc = models.CharField(max_length=100)
    Estado = models.BooleanField(default=True)
    SYNC = models.BooleanField(default=False)

    class Meta:
        db_table = 'Procesos'
        managed = True
        app_label = 'production'
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'

    def __str__(self):
        return self.Nombre_Proc


class Maquinaria(models.Model):
    ID_Maquinaria = models.AutoField(primary_key=True)
    DescripcionMaq = models.CharField(max_length=200, default='')
    AreaMaq = models.CharField(max_length=200, default='Sin Registro')
    Estado = models.BooleanField(default=True)
    SYNC = models.BooleanField(default=False)

    class Meta:
        db_table = 'Maquinaria'
        managed = True
        app_label = 'production'
        verbose_name = 'Maquinaria'
        verbose_name_plural = 'Maquinarias'

    def __str__(self):
        return self.DescripcionMaq


class Clientes(models.Model):
    ID_Cliente = models.AutoField(primary_key=True)
    Cliente = models.CharField(max_length=200)

    class Meta:
        db_table = 'Clientes'
        managed = True
        app_label = 'production'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return self.Cliente

class TipoProducto(models.Model):
    ID_TipoProducto = models.AutoField(primary_key=True)
    DescripcionTipo = models.CharField(max_length=200, default='Descripción por defecto')

    class Meta:
        db_table = 'TipoProducto'
        managed = True
        app_label = 'production'
        verbose_name = 'Tipo de Producto'
        verbose_name_plural = 'Tipos de Producto'

    def __str__(self):
        return self.DescripcionTipo


class Productos(models.Model):
    ID_Producto = models.CharField(max_length=50, primary_key=True)
    DescripcionProd = models.CharField(max_length=200, default='Descripción por defecto')
    ID_TipoProducto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE, db_column='ID_TipoProducto')

    class Meta:
        db_table = 'Productos'
        managed = True
        app_label = 'production'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.DescripcionProd


class ParosProduccion(models.Model):
    ID_Paro = models.AutoField(primary_key=True)
    FechaParo = models.DateField(auto_now_add=True)
    ID_Cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, db_column='ID_Cliente')
    OrdenFabricacionSAP = models.PositiveIntegerField()
    ID_Producto = models.CharField(max_length=50, db_column='ID_Producto')
    HoraInicio = models.TimeField()
    HoraFin = models.TimeField()
    TiempoMuerto = models.PositiveIntegerField()
    PersonasAfectadas = models.FloatField()
    MO = models.FloatField()
    ID_Proceso = models.ForeignKey(Procesos, on_delete=models.CASCADE, db_column='ID_Proceso')
    ID_Maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE, db_column='ID_Maquinaria')
    Causa = models.CharField(max_length=999)
    Diagnostico = models.CharField(max_length=300)
    CausaRaiz = models.CharField(max_length=300)
    Estado = models.BooleanField(default=True)
    SYNC = models.BooleanField(default=False)


    class Meta:
        db_table = 'ParosProduccion'
        managed = True
        app_label = 'production'
        verbose_name = 'ParoProduccion'
        verbose_name_plural = 'ParosProduccion'

    def __str__(self):
        return f"Paro en {self.ID_Proceso.Nombre_Proc} - {self.FechaParo}"
