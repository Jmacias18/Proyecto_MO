# Generated by Django 5.0.9 on 2025-01-03 23:25

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Refrigerador',
            fields=[
                ('id_refrigerador', models.AutoField(db_column='ID_Refrigerador', primary_key=True, serialize=False)),
                ('descripcion_ref', models.CharField(db_column='DescripcionRef', max_length=150)),
                ('min_temp', models.FloatField(db_column='Min')),
                ('max_temp', models.FloatField(db_column='Max')),
                ('tipo_refrigerador', models.CharField(db_column='TipoRefrigerador', max_length=50)),
                ('sync', models.BooleanField(db_column='SYNC', default=False)),
                ('estado', models.BooleanField(db_column='estado')),
            ],
            options={
                'db_table': 'Refrigeradores',
            },
        ),
        migrations.CreateModel(
            name='AutoclaveTemperature',
            fields=[
                ('id_temp_autoclave', models.AutoField(db_column='ID_TempAutoclave', primary_key=True, serialize=False)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('hora', models.TimeField(default=django.utils.timezone.now)),
                ('temp_c', models.FloatField(db_column='TempC')),
                ('temp_f', models.FloatField(db_column='TempF')),
                ('temp_termometro_c', models.FloatField(db_column='TempTermometroC')),
                ('temp_termometro_f', models.FloatField(db_column='TempTermometroF')),
                ('observaciones', models.TextField(blank=True, db_column='Observaciones', null=True)),
                ('inspecciono', models.IntegerField(blank=True, db_column='Inspecciono')),
                ('verificacion', models.IntegerField(blank=True, db_column='Verificacion', null=True)),
                ('sync', models.BooleanField(db_column='SYNC', default=False)),
                ('id_refrigerador', models.ForeignKey(db_column='ID_Refrigerador', on_delete=django.db.models.deletion.CASCADE, to='autoclave.refrigerador')),
            ],
            options={
                'verbose_name': 'Temperatura de Autoclave',
                'verbose_name_plural': 'Temperaturas de Autoclave',
                'db_table': 'TemperaturaAutoclaves',
                'ordering': ['-fecha', '-hora'],
            },
        ),
    ]
