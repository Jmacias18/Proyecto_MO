from django.shortcuts import render, redirect
from .models import Refrigeradores, TemperaturaAreas
from .forms import TempAreaForm, RefrigeradoresForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse
from django.contrib import messages
import pyodbc
from django.db import connections
@login_required
def temperature_control_view(request):
    # Cargar todos los refrigeradores desde la base de datos 'spf_calidad'
    refrigeradores = Refrigeradores.objects.using('spf_calidad').all()
    tipos_refrigeradores = refrigeradores.values_list('TipoRefrigerador', flat=True).distinct()

    # Obtener la fecha seleccionada o usar la fecha de hoy
    today = timezone.localtime(timezone.now()).date()
    selected_date_str = request.GET.get('fecha', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today

    # Filtrar las temperaturas según la fecha seleccionada
    temperaturaareas = TemperaturaAreas.objects.using('spf_calidad').filter(Fecha=selected_date)

    # Obtener los refrigeradores para cada categoría
    refrigeradores_area = refrigeradores.filter(TipoRefrigerador='Area')
    refrigeradores_refrigerador = refrigeradores.filter(TipoRefrigerador='Refrigerador')
    refrigeradores_congelador = refrigeradores.filter(TipoRefrigerador='Congelador')

    # Crear un diccionario para almacenar los colores
    color_temperaturas = {}

    # Crear un diccionario para almacenar los comentarios
    comentarios = {}
    for area in temperaturaareas:
        comentarios[area.ID_Refrigerador.ID_Refrigerador] = area.Comentarios

    for area in temperaturaareas:
        refrigerador = area.ID_Refrigerador

        # Maneja el caso cuando el refrigerador no existe o no está asignado.
        if refrigerador is None:
            color_temperaturas[area.ID_TempAreas] = "gray"  # Color por defecto si no hay refrigerador
            continue  # Salta a la siguiente iteración si no hay refrigerador

        min_temp = refrigerador.Min if refrigerador.Min is not None else 0
        max_temp = refrigerador.Max if refrigerador.Max is not None else 0
        temp = area.Temperatura

        # Asigna un valor predeterminado para que siempre exista
        color = "gray"  # Esto asegura que color siempre tenga un valor

        if temp is None:
            color = "white"
        elif min_temp <= temp <= max_temp:
            color = "green"
        elif min_temp - 3 <= temp < min_temp or max_temp < temp <= max_temp + 3:
            color = "yellow"
        else:
            color = "red"

        # Lógica adicional para "Congeladores"
        if refrigerador.TipoRefrigerador == 'Congelador':
            if temp is None:
                color = "white"
            elif temp > 3.0:  # Mayor que 3
                color = "red"
            elif -15 < temp <= -17:  # Entre 0 y 3
                color = "yellow"
            elif -50 <= temp <= -18:  # Entre -18 y 0
                color = "green"
            elif temp < -51:  # Menor que -51
                color = "red"

        color_temperaturas[area.ID_TempAreas] = color  # Asigna el color al diccionario

    return render(request, 'temperature/temperature.html', {
        'temperaturaareas': temperaturaareas,
        'refrigeradores': refrigeradores,
        'tipos_refrigeradores': tipos_refrigeradores,
        'today': today,
        'selected_date': selected_date,
        'horas': ["07:00", "09:00", "11:00", "13:00", "15:00", "17:00"],
        'color_temperaturas': color_temperaturas,
        'refrigeradores_area': refrigeradores_area,
        'refrigeradores_refrigerador': refrigeradores_refrigerador,
        'refrigeradores_congelador': refrigeradores_congelador,
        'registros_no_sincronizados': temperaturaareas.filter(SYNC=False).count(),
        'comentarios': comentarios  # Pasamos los comentarios al contexto
    })

@login_required
def register_temp_view(request):
    tipos_refrigeradores = ['Refrigerador', 'Congelador']
    refrigeradores = Refrigeradores.objects.using('spf_info').filter(estado=1).all()

    if request.method == 'POST':
        refrigerador_id = request.POST.get('ID_Refrigerador')
        fecha = request.POST.get('Fecha')
        hora = request.POST.get('Hora')
        comentarios = request.POST.get('Comentarios', '')  # Obtenemos los comentarios
        replace = request.POST.get('replace', False)

        # Obtener el refrigerador
        refrigerador = Refrigeradores.objects.using('spf_info').filter(ID_Refrigerador=refrigerador_id).first()
        
        if refrigerador is None or refrigerador.estado == 0:
            messages.error(request, 'No se puede registrar la temperatura, el refrigerador está inactivo o no existe.')
            return redirect('temperature:temperature')

        temperatura = request.POST.get('Temperatura')
        if temperatura:
            temperatura = temperatura.replace(',', '.')

        try:
            temperatura = float(temperatura)
        except ValueError:
            return render(request, 'temperature/error.html', {
                'error': 'El valor de la temperatura no es válido.'
            })

        # Verificar si ya existe un registro para esta fecha y hora
        temperatura_existente = TemperaturaAreas.objects.using('spf_calidad').filter(
            ID_Refrigerador=refrigerador_id,
            Fecha=fecha,
            Hora=hora
        ).first()

        if temperatura_existente and not replace:
            return render(request, 'temperature/confirm_replace.html', {
                'temperatura_existente': temperatura_existente
            })

        # Si es un reemplazo, actualizamos el registro existente
        if replace and temperatura_existente:
            temperatura_existente.Temperatura = temperatura
            temperatura_existente.Comentarios = comentarios  # Guardamos los comentarios
            temperatura_existente.SYNC = False  # Marca como no sincronizado
            temperatura_existente.save(using='spf_calidad')
        else:
            form = TempAreaForm(request.POST)
            if form.is_valid():
                temperatura_area = form.save(commit=False)
                temperatura_area.Temperatura = temperatura
                temperatura_area.Comentarios = comentarios  # Guardamos los comentarios
                temperatura_area.SYNC = False  # Marca como no sincronizado
                temperatura_area.save(using='spf_calidad')
            else:
                messages.error(request, 'Error al guardar la temperatura.')

        return redirect('temperature:temperature')

    else:
        form = TempAreaForm()

    # Filtrar refrigeradores por tipo si se proporciona
    tipo_seleccionado = request.GET.get('tipo')
    if tipo_seleccionado:
        refrigeradores = refrigeradores.filter(TipoRefrigerador=tipo_seleccionado)

    temperaturaareas = TemperaturaAreas.objects.using('spf_calidad').all()

    return render(request, 'temperature/temperature.html', {
        'temperaturaareas': temperaturaareas,
        'refrigeradores': refrigeradores,
        'form': form,
        'tipos_refrigeradores': tipos_refrigeradores,
        'tipo_seleccionado': tipo_seleccionado,
        'horas': ['07:00','11:00', '13:00','15:00','17:00'],  # Horas de ejemplo
    })
@login_required
def edit_temp_view(request, temp_id):
    temperaturaarea = TemperaturaAreas.objects.using('spf_calidad').get(ID_TempAreas=temp_id)
    
    if request.method == 'POST':
        temperatura = request.POST.get('Temperatura')
        
        if temperatura:
            temperatura = temperatura.replace(',', '.')
            try:
                temperatura = float(temperatura)
                temperaturaarea.Temperatura = temperatura
                temperaturaarea.SYNC = False  # Cambia el estado a no sincronizado
                temperaturaarea.save(using='spf_calidad')
                return redirect('temperature:temperature')
            except ValueError:
                return render(request, 'temperature/error.html', {
                    'error': 'El valor de la temperatura no es válido.'
                })

    return render(request, 'temperature/edit_temperature.html', {
        'temperaturaarea': temperaturaarea
    })

@login_required
def delete_temp_view(request, temp_id):
    temperaturaarea = TemperaturaAreas.objects.using('spf_calidad').get(ID_TempAreas=temp_id)
    
    if request.method == 'POST':
        temperaturaarea.delete(using='spf_calidad')
        return redirect('temperature:temperature')

    return render(request, 'temperature/confirm_delete.html', {
        'temperaturaarea': temperaturaarea
    })
@login_required
def register_refrigerador_view(request):
    if request.method == 'POST':
        form = RefrigeradoresForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el nuevo refrigerador
            return redirect('temperature:temperature')  # Redirige a la vista que desees
    else:
        form = RefrigeradoresForm()

    return render(request, 'temperature/register_refrigerador.html', {'form': form})


@login_required
def sync_refrigeradores_view(request):
    refrigeradores_no_sync = Refrigeradores.objects.using('spf_info').filter(SYNC=False)

    server_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=QBSERVER\\SQLEXPRESS;"
        "Database=SPF_Info;"
        "UID=it;"
        "PWD=sqlSPF#2024;"
    )

    if not refrigeradores_no_sync.exists():
        messages.warning(request, 'No hay refrigeradores para sincronizar.')
        return JsonResponse({'message': 'No hay refrigeradores para sincronizar.'}, status=200)

    try:
        with pyodbc.connect(server_conn_str) as conn:
            cursor = conn.cursor()
            print("Conexión exitosa al servidor y base de datos.")

            for refrigerador in refrigeradores_no_sync:
                # Aquí puedes agregar lógica para verificar si el refrigerador existe en el servidor
                # Por ejemplo, puedes hacer un SELECT para ver si ya existe
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM Refrigeradores
                    WHERE ID_Refrigerador = ?
                """, (refrigerador.ID_Refrigerador,))
                
                existe = cursor.fetchone()[0] > 0

                if existe:
                    cursor.execute("""
                        UPDATE Refrigeradores
                        SET SYNC = 1  -- Marca como sincronizado
                        WHERE ID_Refrigerador = ?
                    """, (refrigerador.ID_Refrigerador,))
                else:
                    cursor.execute("""
                        INSERT INTO Refrigeradores (ID_Refrigerador, DescripcionRef, Min, Max, TipoRefrigerador, SYNC, estado)
                        VALUES (?, ?, ?, ?, ?, 1, ?)
                    """, (refrigerador.ID_Refrigerador, refrigerador.DescripcionRef, refrigerador.Min, refrigerador.Max, refrigerador.TipoRefrigerador, refrigerador.estado))

                refrigerador.SYNC = True
                refrigerador.save(using='spf_info')

            conn.commit()
            messages.success(request, 'Sincronización completa de refrigeradores.')

    except Exception as e:
        print(f'Error al conectar o sincronizar: {str(e)}')
        messages.error(request, f'Error al sincronizar los datos: {str(e)}')
        return JsonResponse({'message': f'Error al sincronizar los datos: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Sincronización completa'}, status=200)

@login_required
def sync_data_view(request):
    registros_no_sync = TemperaturaAreas.objects.using('spf_calidad').filter(SYNC=False)

    server_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=QBSERVER\\SQLEXPRESS;"
        "Database=SPF_Calidad;"
        "UID=it;"
        "PWD=sqlSPF#2024;"
    )

    if not registros_no_sync.exists():
        messages.warning(request, 'No hay registros para sincronizar.')
        return JsonResponse({'message': 'No hay registros para sincronizar.'}, status=200)

    try:
        with pyodbc.connect(server_conn_str) as conn:
            cursor = conn.cursor()
            print("Conexión exitosa al servidor y base de datos.")

            for registro in registros_no_sync:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM TemperaturaAreas
                    WHERE Fecha = ? AND Hora = ? AND ID_Refrigerador = ?
                """, (registro.Fecha, registro.Hora, registro.ID_Refrigerador.ID_Refrigerador))
                
                existe = cursor.fetchone()[0] > 0

                if existe:
                    # Si el registro ya existe, actualizamos la temperatura y los comentarios
                    cursor.execute("""
                        UPDATE TemperaturaAreas
                        SET Temperatura = ?, Comentarios = ?, SYNC = ?
                        WHERE Fecha = ? AND Hora = ? AND ID_Refrigerador = ?
                    """, (
                        registro.Temperatura, 
                        registro.Comentarios,  # Sincronizamos los comentarios
                        True, 
                        registro.Fecha, 
                        registro.Hora, 
                        registro.ID_Refrigerador.ID_Refrigerador
                    ))
                else:
                    # Si el registro no existe, lo insertamos con la temperatura y los comentarios
                    cursor.execute("""
                        INSERT INTO TemperaturaAreas (Fecha, Hora, ID_Refrigerador, Temperatura, Comentarios, SYNC)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        registro.Fecha, 
                        registro.Hora, 
                        registro.ID_Refrigerador.ID_Refrigerador, 
                        registro.Temperatura, 
                        registro.Comentarios,  # Insertamos los comentarios
                        True
                    ))

                # Actualizamos el campo SYNC en la base de datos local después de la sincronización
                registro.SYNC = True
                registro.save(using='spf_calidad')

            conn.commit()
            messages.success(request, 'Sincronización completa')

    except Exception as e:
        print(f'Error al conectar o sincronizar: {str(e)}')
        messages.error(request, f'Error al sincronizar los datos: {str(e)}')
        return JsonResponse({'message': f'Error al sincronizar los datos: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Sincronización completa'}, status=200)