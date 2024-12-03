from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .forms import HorasProcesosForm
from procesos.models import Empleados, Procesos
from .models import Horasprocesos
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess
import json
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages


def gestion_horas_procesos(request):
    if request.method == 'POST':
        for empleado in Empleados.objects.all():
            codigo_emp = empleado.codigo_emp
            inasistencia = request.POST.get(f'inasistencia_{codigo_emp}', 'off') == 'on'
            asistencia = 0 if inasistencia else 1
            horas_extras = request.POST.get(f'horas_extras_{codigo_emp}', 0)
            horas_extras = float(horas_extras) if horas_extras and horas_extras.strip() else 0

            if inasistencia:
                # Insert a single record with zero hours
                Horasprocesos.objects.create(
                    fecha_hrspro=timezone.now().date(),
                    codigo_emp=empleado,
                    asistencia=asistencia,
                    id_pro=0,
                    horaentrada='00:00:00',
                    horasalida='00:00:00',
                    hrs=0,
                    totalhrs=0,
                    hrsextras=0,
                    autorizado=False,
                    sync=False
                )
            else:
                for i in range(1, 7):
                    id_proceso = request.POST.get(f'proceso{i}_header')
                    hora_entrada = request.POST.get(f'inicio_proceso{i}_{codigo_emp}') or None
                    hora_salida = request.POST.get(f'fin_proceso{i}_{codigo_emp}') or None

                    if id_proceso and hora_entrada and hora_salida:
                        # Calcular las horas trabajadas
                        formato = '%H:%M'
                        hora_entrada_dt = datetime.strptime(hora_entrada, formato)
                        hora_salida_dt = datetime.strptime(hora_salida, formato)
                        diferencia = hora_salida_dt - hora_entrada_dt
                        horas_trabajadas = diferencia.total_seconds() / 3600

                        Horasprocesos.objects.create(
                            fecha_hrspro=timezone.now().date(),
                            codigo_emp=empleado,
                            asistencia=asistencia,
                            id_pro=id_proceso,
                            horaentrada=hora_entrada,
                            horasalida=hora_salida,
                            hrs=horas_trabajadas,
                            totalhrs=horas_trabajadas + horas_extras,
                            hrsextras=horas_extras,
                            autorizado=False,
                            sync=False
                        )
        messages.success(request, '¡Las horas de los procesos se registraron exitosamente!')    
        return redirect('horas_procesos:gestion_horas_procesos')
    else:
        form = HorasProcesosForm()
    
    empleados = Empleados.objects.all()
    procesos = Procesos.objects.filter(estado_pro=True)  # Filtrar solo los procesos activos
    departamentos = Empleados.objects.values_list('depto_emp', flat=True).distinct()
    rango_procesos = range(1, 7)  # Generar el rango de números del 1 al 6
    return render(request, 'horas_procesos/gestion_horas_procesos.html', {
        'form': form,
        'empleados': empleados,
        'procesos': procesos,
        'departamentos': departamentos,
        'rango_procesos': rango_procesos,  # Pasar el rango al contexto
    })
@csrf_exempt
def sync_to_server_view(request):
    if request.method == 'POST':
        try:
            # Obtener la ruta absoluta del script de sincronización
            script_path = os.path.join(os.path.dirname(__file__), 'sync_db_to_server.py')
            # Ejecutar el script de sincronización
            subprocess.run(['python', script_path], check=True)
            return JsonResponse({'status': 'success', 'message': 'Sincronización completada con éxito.'})
        except subprocess.CalledProcessError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

from django.shortcuts import render
from .models import Horasprocesos, Empleados
from collections import defaultdict
from datetime import date

def actualizar_horas_procesos(request):
    departamento_seleccionado = request.GET.get('departamento', None)
    fecha_seleccionada = request.GET.get('fecha', None)
    
    registros_combinados = []
    if departamento_seleccionado or fecha_seleccionada:
        registros = Horasprocesos.objects.all()
        empleados = Empleados.objects.all()
        empleados_dict = {empleado.codigo_emp: empleado.depto_emp for empleado in empleados}

        if departamento_seleccionado and departamento_seleccionado != "":
            empleados = empleados.filter(depto_emp=departamento_seleccionado)
            registros = registros.filter(codigo_emp__depto_emp=departamento_seleccionado)
        
        if fecha_seleccionada:
            try:
                fecha_seleccionada = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
                registros = registros.filter(fecha_hrspro=fecha_seleccionada)
            except ValueError:
                messages.error(request, 'Formato de fecha no válido. Use el formato YYYY-MM-DD.')

        # Agrupar registros por empleado
        registros_por_empleado = defaultdict(list)
        for registro in registros:
            registros_por_empleado[registro.codigo_emp.codigo_emp].append(registro)

        # Crear una lista de registros combinados
        for codigo_emp, registros in registros_por_empleado.items():
            registro_combinado = {
                'codigo_emp': codigo_emp,
                'nombre_emp': registros[0].codigo_emp.nombre_emp,
                'depto_emp': empleados_dict[codigo_emp],
                'procesos': registros
            }
            registros_combinados.append(registro_combinado)

    departamentos = Empleados.objects.values_list('depto_emp', flat=True).distinct()
    procesos = Procesos.objects.all()

    if request.method == 'POST':
        eliminar_ids = []
        for key, value in request.POST.items():
            if key.startswith('horaentrada_'):
                id_hrspro = key.split('_')[1]
                proceso = Horasprocesos.objects.get(id_hrspro=id_hrspro)
                proceso.horaentrada = request.POST.get(f'horaentrada_{id_hrspro}')
                proceso.horasalida = request.POST.get(f'horasalida_{id_hrspro}')
                proceso.hrs = request.POST.get(f'hrs_{id_hrspro}')
                proceso.totalhrs = request.POST.get(f'totalhrs_{id_hrspro}')
                proceso.hrsextras = request.POST.get(f'hrsextras_{id_hrspro}')
                proceso.asistencia = 0 if request.POST.get(f'inasistencia_{id_hrspro}') else 1
                proceso.id_pro = request.POST.get(f'proceso_{id_hrspro}')  # Actualizar el proceso
                if proceso.asistencia == 0:
                    proceso.horaentrada = '00:00:00.0000000'
                    proceso.horasalida = '00:00:00.0000000'
                    proceso.hrs = 0
                    proceso.totalhrs = 0
                    proceso.hrsextras = 0
                    proceso.id_pro = 0
                proceso.save()
                print(f"Updated proceso {id_hrspro}: asistencia={proceso.asistencia}, horaentrada={proceso.horaentrada}, horasalida={proceso.horasalida}")
            elif key.startswith('eliminar_') and value == 'on':
                eliminar_ids.append(key.split('_')[1])
        
        for id_hrspro in eliminar_ids:
            proceso = Horasprocesos.objects.get(id_hrspro=id_hrspro)
            proceso.delete()
            print(f"Deleted proceso {id_hrspro}")

        messages.success(request, '¡El proceso se actualizó exitosamente!')
        return redirect(reverse('horas_procesos:actualizar_horas_procesos'))
    
    return render(request, 'horas_procesos/actualizar_horas_procesos.html', {
        'registros_combinados': registros_combinados,
        'departamentos': departamentos,
        'procesos': procesos,
        'departamento_seleccionado': departamento_seleccionado,
        'fecha_seleccionada': fecha_seleccionada,
    })
@csrf_exempt
def eliminar_proceso(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])
        for id_hrspro in ids:
            registro = get_object_or_404(Horasprocesos, id_hrspro=id_hrspro)
            registro.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

from django.http import HttpResponse
import csv


def exportar_excel(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="horas_procesos.csv"'

    writer = csv.writer(response)
    writer.writerow(['Código Emp', 'Empleado', 'Departamento', 'Proceso', 'Hora Entrada', 'Hora Salida', 'Hrs', 'Total Hrs', 'Hrs Extras', 'Inasistencia'])

    registros = Horasprocesos.objects.all()
    for registro in registros:
        writer.writerow([registro.codigo_emp.codigo_emp, registro.codigo_emp.nombre_emp, registro.codigo_emp.depto_emp, registro.id_pro, registro.horaentrada, registro.horasalida, registro.hrs, registro.totalhrs, registro.hrsextras, registro.asistencia])

    return response