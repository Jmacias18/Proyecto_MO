from django.shortcuts import render
from .forms import HorasProcesosForm
from procesos.models import Empleados, Procesos

def gestion_horas_procesos(request):
    if request.method == 'POST':
        form = HorasProcesosForm(request.POST)
        if form.is_valid():
            # Procesar los datos del formulario
            # Aquí puedes guardar los datos en la base de datos o realizar otras acciones
            pass
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