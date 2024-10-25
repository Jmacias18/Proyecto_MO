from django.shortcuts import render, redirect
from .forms import HorasProcesosForm
from procesos.models import Empleados, Procesos
from .models import Horasprocesos
from django.utils import timezone

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