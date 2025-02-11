# Generated by Django 5.0.9 on 2025-01-03 23:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clientes',
            fields=[
                ('ID_Cliente', models.AutoField(primary_key=True, serialize=False)),
                ('Cliente', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'db_table': 'Clientes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Maquinaria',
            fields=[
                ('ID_Maquinaria', models.AutoField(primary_key=True, serialize=False)),
                ('DescripcionMaq', models.CharField(default='', max_length=200)),
                ('AreaMaq', models.CharField(default='Sin Registro', max_length=200)),
                ('Estado', models.BooleanField(default=True)),
                ('SYNC', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Maquinaria',
                'verbose_name_plural': 'Maquinarias',
                'db_table': 'Maquinaria',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Procesos',
            fields=[
                ('ID_Proc', models.AutoField(primary_key=True, serialize=False)),
                ('Nombre_Proc', models.CharField(max_length=100)),
                ('Estado', models.BooleanField(default=True)),
                ('SYNC', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Proceso',
                'verbose_name_plural': 'Procesos',
                'db_table': 'Procesos',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TipoProducto',
            fields=[
                ('ID_TipoProducto', models.AutoField(primary_key=True, serialize=False)),
                ('DescripcionTipo', models.CharField(default='Descripción por defecto', max_length=200)),
            ],
            options={
                'verbose_name': 'Tipo de Producto',
                'verbose_name_plural': 'Tipos de Producto',
                'db_table': 'TipoProducto',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ParosProduccion',
            fields=[
                ('ID_Paro', models.AutoField(primary_key=True, serialize=False)),
                ('FechaParo', models.DateField(auto_now_add=True)),
                ('OrdenFabricacionSAP', models.PositiveIntegerField()),
                ('ID_Producto', models.CharField(db_column='ID_Producto', max_length=50)),
                ('HoraInicio', models.TimeField()),
                ('HoraFin', models.TimeField()),
                ('TiempoMuerto', models.PositiveIntegerField()),
                ('PersonasAfectadas', models.FloatField()),
                ('MO', models.FloatField()),
                ('Causa', models.CharField(max_length=999)),
                ('Diagnostico', models.CharField(max_length=300)),
                ('CausaRaiz', models.CharField(max_length=300)),
                ('Estado', models.BooleanField(default=True)),
                ('SYNC', models.BooleanField(default=False)),
                ('ID_Cliente', models.ForeignKey(db_column='ID_Cliente', on_delete=django.db.models.deletion.CASCADE, to='production.clientes')),
                ('ID_Maquinaria', models.ForeignKey(db_column='ID_Maquinaria', on_delete=django.db.models.deletion.CASCADE, to='production.maquinaria')),
                ('ID_Proceso', models.ForeignKey(db_column='ID_Proceso', on_delete=django.db.models.deletion.CASCADE, to='production.procesos')),
            ],
            options={
                'verbose_name': 'ParoProduccion',
                'verbose_name_plural': 'ParosProduccion',
                'db_table': 'ParosProduccion',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Productos',
            fields=[
                ('ID_Producto', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('DescripcionProd', models.CharField(default='Descripción por defecto', max_length=200)),
                ('ID_TipoProducto', models.ForeignKey(db_column='ID_TipoProducto', on_delete=django.db.models.deletion.CASCADE, to='production.tipoproducto')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'db_table': 'Productos',
                'managed': True,
            },
        ),
    ]
