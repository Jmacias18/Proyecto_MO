from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .forms import AutoclaveTemperatureForm
from django.http import JsonResponse
from .models import AutoclaveTemperature, Refrigerador
from django.contrib.auth.mixins import LoginRequiredMixin  # Importante para asegurar que el usuario esté logueado
from usuarios.models import CustomUser
from django.contrib.auth.decorators import login_required
import pyodbc, json

class AutoclaveTemperatureListView(ListView):
    model = AutoclaveTemperature
    template_name = 'autoclave/temperature_list.html'
    context_object_name = 'temperatures'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()

        # Obtener la fecha de la solicitud GET (si está presente)
        fecha = self.request.GET.get('fecha', None)

        # Filtrar por fecha si el parámetro 'fecha' está presente
        if fecha:
            queryset = queryset.filter(fecha=fecha)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener el nombre del supervisor logueado
        supervisor_name = self.request.user.get_full_name()
        context['supervisor_name'] = supervisor_name

        # Verificar si el usuario es del grupo 'Editor'
        is_editor = self.request.user.groups.filter(name='Editor').exists()
        context['is_editor'] = is_editor

        # Iterar sobre todas las temperaturas para obtener los nombres de los supervisores
        for temperature in context['temperatures']:
            if temperature.inspecciono:
                user = get_object_or_404(CustomUser, id=temperature.inspecciono)
                temperature.inspecciono = user.get_full_name()

            if temperature.verificacion:
                supervisor = get_object_or_404(CustomUser, id=temperature.verificacion)
                temperature.verificacion = supervisor.get_full_name()

        return context

# Vista para crear una nueva temperatura
class AutoclaveTemperatureCreateView(LoginRequiredMixin, CreateView):
    model = AutoclaveTemperature
    form_class = AutoclaveTemperatureForm
    template_name = 'autoclave/temperature_form.html'
    success_url = reverse_lazy('autoclave:temperature_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos los refrigeradores al contexto para que estén disponibles en la plantilla
        context['refrigeradores'] = Refrigerador.objects.all()  # Obtén todos los refrigeradores
        return context

    def form_valid(self, form):
        # Obtener el ID del refrigerador desde el formulario
        id_refrigerador = form.cleaned_data.get('id_refrigerador')

        # Buscar la instancia del Refrigerador correspondiente
        refrigerador_instance = Refrigerador.objects.get(id_refrigerador=id_refrigerador)

        # Asignar la instancia del refrigerador al campo id_refrigerador
        form.instance.id_refrigerador = refrigerador_instance

        # Realizar la conversión de temperatura (si aplica)
        temp_c = form.cleaned_data.get('temp_c')
        temp_termometro_c = form.cleaned_data.get('temp_termometro_c')

        if temp_c is not None:
            form.instance.temp_f = (temp_c * 9/5) + 32
        if temp_termometro_c is not None:
            form.instance.temp_termometro_f = (temp_termometro_c * 9/5) + 32

        # Obtener el ID del usuario logueado
        user_id = self.request.user.id  # Obtenemos el ID del usuario logueado

        # Asignar el usuario al campo 'Inspecciono'
        form.instance.inspecciono = user_id

        # Llamar al método original form_valid para guardar el objeto
        response = super().form_valid(form)
        messages.success(self.request, "¡Temperatura registrada exitosamente!")
        return response


    
# Vista para sincronizar los datos con la base de datos remota
@login_required
def sync_data_view(request):
    try:
        # Filtramos los registros que no están sincronizados
        registros_no_sync = AutoclaveTemperature.objects.filter(sync=False)

        if registros_no_sync.count() == 0:
            # Si no hay registros para sincronizar, devolvemos un mensaje adecuado
            return JsonResponse({
                'message': 'No hay registros por sincronizar',
                'status': 'warning',
                'records_status': 'No hay registros por sincronizar'
            }, status=200)

        # Cadena de conexión al servidor de base de datos SQL Server
        server_conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=QBSERVER\\SQLEXPRESS;"  # Nombre correcto del servidor
            "Database=SPF_Calidad;"  # Nombre correcto de la base de datos
            "UID=it;"  # Usuario
            "PWD=sqlSPF#2024;"  # Contraseña
        )

        # Intentamos conectarnos a la base de datos remota
        with pyodbc.connect(server_conn_str) as conn:
            cursor = conn.cursor()
            print("Conexión exitosa al servidor y base de datos.")

            for registro in registros_no_sync:
                if registro.id_refrigerador is None:
                    # Registro no tiene refrigerador asignado
                    messages.warning(request, f'Registro con fecha {registro.fecha} y hora {registro.hora} no tiene refrigerador asignado.')
                    continue  # Saltamos este registro

                cursor.execute("""SELECT COUNT(*) FROM TemperaturaAutoclaves WHERE Fecha = ? AND Hora = ? AND ID_Refrigerador = ?""", 
                               (registro.fecha, registro.hora, registro.id_refrigerador.id_refrigerador))

                existe = cursor.fetchone()[0] > 0

                if existe:
                    # Si el registro existe, actualizamos todos los campos incluyendo verificacion
                    cursor.execute("""UPDATE TemperaturaAutoclaves SET 
                                       TempC = ?, TempF = ?, TempTermometroC = ?, TempTermometroF = ?, Observaciones = ?, 
                                       SYNC = 1, Inspecciono = ?, Verificacion = ?  -- Agregar el campo Verificacion
                                       WHERE Fecha = ? AND Hora = ? AND ID_Refrigerador = ?""",
                                   (registro.temp_c, registro.temp_f, registro.temp_termometro_c,
                                    registro.temp_termometro_f, registro.observaciones,
                                    registro.inspecciono if registro.inspecciono else 0,
                                    registro.verificacion if registro.verificacion is not None else 0,  # Asegúrate de pasar el valor de verificación
                                    registro.fecha, registro.hora, registro.id_refrigerador.id_refrigerador))
                else:
                    # Si el registro no existe, lo insertamos con todos los campos incluyendo verificacion
                    cursor.execute("""INSERT INTO TemperaturaAutoclaves (Fecha, Hora, ID_Refrigerador, TempC, TempF, 
                                       TempTermometroC, TempTermometroF, Observaciones, SYNC, Inspecciono, Verificacion)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""", 
                                   (registro.fecha, registro.hora, registro.id_refrigerador.id_refrigerador,
                                    registro.temp_c, registro.temp_f, registro.temp_termometro_c,
                                    registro.temp_termometro_f, registro.observaciones,
                                    registro.inspecciono if registro.inspecciono else 0,
                                    registro.verificacion if registro.verificacion is not None else 0))  # Asegúrate de pasar el valor de verificación

                # Actualizamos el campo SYNC en la base de datos local
                registro.sync = True
                registro.save()

            conn.commit()  # Confirmamos los cambios en la base de datos remota
            return JsonResponse({
                'message': 'Sincronización completa',
                'status': 'success',
                'records_status': 'Existen registros por sincronizar'
            }, status=200)

    except pyodbc.Error as e:
        # Error específico de conexión a la base de datos
        print(f'Error de conexión con la base de datos: {str(e)}')
        return JsonResponse({
            'message': f'Error al conectar con la base de datos. Verifica la conexión al servidor SQL: {str(e)}',
            'status': 'error',
            'records_status': ''
        }, status=500)

    except Exception as e:
        # Cualquier otro error genérico
        print(f'Error al conectar o sincronizar: {str(e)}')
        return JsonResponse({
            'message': f'Error al sincronizar los datos: {str(e)}',
            'status': 'error',
            'records_status': ''
        }, status=500)



@login_required
def temperature_edit(request, id_temp_autoclave):
    # Obtener el objeto AutoclaveTemperature a editar
    temperature = get_object_or_404(AutoclaveTemperature, id_temp_autoclave=id_temp_autoclave)

    # Si el formulario es enviado con POST
    if request.method == 'POST':
        form = AutoclaveTemperatureForm(request.POST, instance=temperature)
        if form.is_valid():
            # Desactivar la sincronización cuando se modifica
            temperature.sync = False
            form.save()  # Guardar los cambios
            return redirect('autoclave:temperature_list')  # Redirigir al listado después de guardar
    else:
        # Si es un GET, cargar el formulario con la instancia del objeto
        form = AutoclaveTemperatureForm(instance=temperature)
    
    # Renderizar la plantilla con el formulario y el objeto
    return render(request, 'autoclave/temperature_edit.html', {
        'form': form,
        'temperature': temperature  # Pasar el objeto a la plantilla para usarlo si es necesario
    })

def temperature_delete(request, id_temp_autoclave):
    temperature = get_object_or_404(AutoclaveTemperature, id_temp_autoclave=id_temp_autoclave)
    
    if request.method == 'POST':
        temperature.delete()
        return redirect('autoclave:temperature_list')
    
    return render(request, 'autoclave/temperature_confirm_delete.html', {'temperature': temperature})

def get_sync_status(request):
    # Lógica para contar los registros no sincronizados
    registros_no_sincronizados = AutoclaveTemperature.objects.filter(sincronizado=False).count()
    return JsonResponse({
        'registros_no_sincronizados': registros_no_sincronizados,
    })

def temperature_list(request):
    # Contamos los registros que no están sincronizados
    registros_no_sincronizados = AutoclaveTemperature.objects.filter(sync=False).count()

    # Depuración: Verificar el conteo
    print(f"Registros no sincronizados: {registros_no_sincronizados}")  # Aquí estamos imprimiendo el valor para ver si se calcula correctamente

    # Pasamos los datos necesarios al template
    return render(request, 'autoclave/temperature_list.html', {
        'registros_no_sincronizados': registros_no_sincronizados
    })

@login_required
def update_verification(request):
    # Verificar si el usuario es supervisor
    if not request.user.is_supervisor:
        return JsonResponse({'status': 'error', 'message': 'No tienes permisos para realizar esta acción.'}, status=403)

    # Obtener el ID de la temperatura y el estado de la verificación
    try:
        data = json.loads(request.body)
        temperature_id = data.get('temperature_id')
        verification_status = data.get('verification_status')

        # Obtener la instancia de AutoclaveTemperature
        temperature = AutoclaveTemperature.objects.get(id_temp_autoclave=temperature_id)

        # Si la verificación está activada (True), asignamos el ID del supervisor
        if verification_status == 'True':
            temperature.verificacion = request.user.id  # Asignamos el ID del supervisor
        else:
            temperature.verificacion = None  # Si desmarca el checkbox, limpiamos el campo

        temperature.save()
        return JsonResponse({'status': 'success', 'message': 'Verificación actualizada correctamente.'})

    except AutoclaveTemperature.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Temperatura no encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
