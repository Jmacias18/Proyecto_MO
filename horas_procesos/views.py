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
from django.http import JsonResponse
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
    
    registros = Horasprocesos.objects.all()
    empleados = Empleados.objects.all()
    empleados_dict = {empleado.codigo_emp: empleado.depto_emp for empleado in empleados}

    if departamento_seleccionado:
        empleados = empleados.filter(depto_emp=departamento_seleccionado)
        registros = registros.filter(codigo_emp__depto_emp=departamento_seleccionado)
    
    if fecha_seleccionada:
        fecha_seleccionada = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
        registros = registros.filter(fecha_hrspro=fecha_seleccionada)

    # Agrupar registros por empleado
    registros_por_empleado = defaultdict(list)
    for registro in registros:
        registros_por_empleado[registro.codigo_emp.codigo_emp].append(registro)

    # Crear una lista de registros combinados
    registros_combinados = []
    for codigo_emp, registros in registros_por_empleado.items():
        registro_combinado = {
            'codigo_emp': codigo_emp,
            'nombre_emp': registros[0].codigo_emp.nombre_emp,
            'depto_emp': empleados_dict[codigo_emp],
            'procesos': registros
        }
        registros_combinados.append(registro_combinado)

    departamentos = Empleados.objects.values_list('depto_emp', flat=True).distinct()

    if request.method == 'POST':
        if 'edit' in request.POST:
            # Editar registro
            registro_id = request.POST.get('edit')
            registro = get_object_or_404(Horasprocesos, id_hrspro=registro_id)
            registro.horaentrada = request.POST.get(f'horaentrada_{registro_id}')
            registro.horasalida = request.POST.get(f'horasalida_{registro_id}')
            registro.hrs = float(request.POST.get(f'hrs_{registro_id}').replace(',', '.'))
            registro.totalhrs = float(request.POST.get(f'totalhrs_{registro_id}').replace(',', '.'))
            registro.hrsextras = float(request.POST.get(f'hrsextras_{registro_id}').replace(',', '.'))
            registro.asistencia = 0 if request.POST.get(f'inasistencia_{registro_id}') else 1
            registro.save()
            return redirect('horas_procesos:actualizar_horas_procesos')
        elif 'delete' in request.POST:
            # Eliminar registro
            registro_id = request.POST.get('delete')
            registro = get_object_or_404(Horasprocesos, id_hrspro=registro_id)
            registro.delete()
            return redirect('horas_procesos:actualizar_horas_procesos')

    return render(request, 'horas_procesos/actualizar_horas_procesos.html', {
        'registros_combinados': registros_combinados,
        'departamentos': departamentos,
        'departamento_seleccionado': departamento_seleccionado,
        'fecha_seleccionada': fecha_seleccionada,
    })