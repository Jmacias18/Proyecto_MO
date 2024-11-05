from django.shortcuts import render, redirect
from .forms import HorasProcesosForm
from procesos.models import Empleados, Procesos
from .models import Horasprocesos
from django.utils import timezone
import subprocess
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
                    total_hrs_proceso = request.POST.get(f'total_proceso{i}_{codigo_emp}', None)
                    total_hrs_proceso = float(total_hrs_proceso) if total_hrs_proceso and total_hrs_proceso.strip() else 0

                    if id_proceso and hora_entrada and hora_salida:
                        Horasprocesos.objects.create(
                            fecha_hrspro=timezone.now().date(),
                            codigo_emp=empleado,
                            asistencia=asistencia,
                            id_pro=id_proceso,
                            horaentrada=hora_entrada,
                            horasalida=hora_salida,
                            hrs=total_hrs_proceso,
                            totalhrs=total_hrs_proceso + horas_extras, 
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
    return render(request, 'horas_procesos/gestion_horas_procesos.html', {
        'form': form,
        'empleados': empleados,
        'procesos': procesos,
        'departamentos': departamentos,
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


def editar_registros(request):
    # Lógica de la vista para editar registros pasados
    departamentos = Empleados.objects.values_list('depto_emp', flat=True).distinct()
    return render(request, 'horas_procesos/editar_registros.html', {'departamentos': departamentos})

def obtener_registros(request):
    fecha = request.GET.get('fecha')
    departamento = request.GET.get('departamento')
    
    empleados = Empleados.objects.filter(depto_emp=departamento)
    registros_data = []
    for empleado in empleados:
        registros = Horasprocesos.objects.filter(fecha_hrspro=fecha, codigo_emp=empleado)
        registro_data = {
            'codigo_emp': empleado.codigo_emp,
            'nombre_emp': empleado.nombre_emp,
            'depto_emp': empleado.depto_emp,
            'asistencia': False,
            'hrsextras': 0,
            'totalhrs': 0
        }
        for i in range(1, 7):
            proceso = registros.filter(id_pro=i).first()
            if proceso:
                registro_data[f'inicio_proceso{i}'] = proceso.horaentrada
                registro_data[f'fin_proceso{i}'] = proceso.horasalida
                registro_data[f'total_proceso{i}'] = proceso.hrs
                registro_data['asistencia'] = proceso.asistencia
                registro_data['hrsextras'] = proceso.hrsextras
                registro_data['totalhrs'] = proceso.totalhrs
        registros_data.append(registro_data)
    return JsonResponse({'registros': registros_data})