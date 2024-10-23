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
            horas_extras = request.POST.get(f'horas_extras_{codigo_emp}', None)
            horas_extras = float(horas_extras) if horas_extras and horas_extras.strip() else None

            for i in range(1, 7):
                id_proceso = request.POST.get(f'proceso{i}_header')
                hora_entrada = request.POST.get(f'inicio_proceso{i}_{codigo_emp}') or None
                hora_salida = request.POST.get(f'fin_proceso{i}_{codigo_emp}') or None
                total_hrs_proceso = request.POST.get(f'total_proceso{i}_{codigo_emp}', None)
                total_hrs_proceso = float(total_hrs_proceso) if total_hrs_proceso and total_hrs_proceso.strip() else None

                if id_proceso and hora_entrada and hora_salida:
                    empleado_instance = Empleados.objects.get(codigo_emp=codigo_emp)
                    Horasprocesos.objects.create(
                        fecha_hrspro=timezone.now().date(),
                        codigo_emp=empleado_instance,
                        asistencia=asistencia,
                        id_pro=id_proceso,
                        horaentrada=hora_entrada,
                        horasalida=hora_salida,
                        hrs=total_hrs_proceso,
                        totalhrs=total_hrs_proceso,
                        hrsextras=horas_extras,
                        autorizado=False,
                        sync=False
                    )
        return redirect('horas_procesos:gestion_horas_procesos')
    else:
        form = HorasProcesosForm()
    
    empleados = Empleados.objects.all()
    procesos = Procesos.objects.all()
    departamentos = Empleados.objects.values_list('depto_emp', flat=True).distinct()
    return render(request, 'horas_procesos/gestion_horas_procesos.html', {
        'form': form,
        'empleados': empleados,
        'procesos': procesos,
        'departamentos': departamentos,
    })