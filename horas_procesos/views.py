from datetime import datetime, date
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
import pyodbc
from collections import defaultdict

# Conexión a la base de datos SPF_Info
spf_info_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'SPF_Info',
    'trusted_connection': 'yes'
}

def get_spf_info_connection():
    return pyodbc.connect(
        driver=spf_info_conn_info['driver'],
        server=spf_info_conn_info['server'],
        database=spf_info_conn_info['database'],
        trusted_connection=spf_info_conn_info['trusted_connection']
    )


def gestion_horas_procesos(request):
    if request.method == 'POST':
        # Obtener los tipos de inasistencia de la base de datos SPF_Info
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
        tipos_inasistencia = cursor.fetchall()
        spf_info_conn.close()

        # Crear un diccionario para mapear la descripción al ID_Asis
        descripcion_a_id = {tipo[1]: tipo[0] for tipo in tipos_inasistencia}

        for empleado in Empleados.objects.all():
            codigo_emp = empleado.codigo_emp
            tipo_inasistencia = request.POST.get(f'tipo_inasistencia_{codigo_emp}', '')  # Obtener el tipo de inasistencia
            ID_Asis = tipo_inasistencia if tipo_inasistencia else None
            inasistencia = ID_Asis in descripcion_a_id.values()  # Verificar si es una inasistencia
            horas_extras = request.POST.get(f'horas_extras_{codigo_emp}', 0)
            horas_extras = float(horas_extras) if horas_extras and horas_extras.strip() else 0

            if inasistencia and tipo_inasistencia not in ['NI', 'RT','ASI']:
                # Insert a single record with zero hours
                Horasprocesos.objects.create(
                    fecha_hrspro=timezone.now().date(),
                    codigo_emp=empleado,
                    ID_Asis=ID_Asis,
                    id_pro=0,
                    horaentrada='00:00:00',
                    horasalida='00:00:00',
                    hrs=0,
                    totalhrs=0,
                    hrsextras=0,
                    autorizado=False,
                    sync=False,
                    ucreado=request.user.username,  # Guardar el usuario que creó el registro
                    umod=None,  # Guardar el usuario que modificó el registro
                    fmod=None
                )
            
            else:
                for i in range(1, 16):
                    id_proceso = request.POST.get(f'proceso{i}_header')
                    hora_entrada = request.POST.get(f'inicio_proceso{i}_{codigo_emp}') or None
                    hora_salida = request.POST.get(f'fin_proceso{i}_{codigo_emp}') or None
                    id_producto = request.POST.get(f'producto{i}_header')

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
                            ID_Asis=ID_Asis,
                            id_pro=id_proceso,
                            id_producto=id_producto,  
                            horaentrada=hora_entrada,
                            horasalida=hora_salida,
                            hrs=horas_trabajadas,
                            totalhrs=horas_trabajadas + horas_extras,
                            hrsextras=horas_extras,
                            autorizado=False,
                            sync=False,
                            ucreado=request.user.username,  # Guardar el usuario que creó el registro
                            umod=None,  # Guardar el usuario que modificó el registro
                            fmod=None
                        )
        messages.success(request, '¡Las horas de los procesos se registraron exitosamente!')    
        return redirect('horas_procesos:gestion_horas_procesos')
    else:
        form = HorasProcesosForm()
    
    empleados = Empleados.objects.all()
    procesos = Procesos.objects.filter(estado_pro=True)  # Filtrar solo los procesos activos
    departamentos = Empleados.objects.values_list('depto_emp', flat=True).distinct()
    rango_procesos = range(1, 16)  # Generar el rango de números del 1 al 16

    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Producto, DescripcionProd FROM Productos")
    productos = cursor.fetchall()
    
    # Obtener los tipos de inasistencia de la base de datos SPF_Info
    cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
    tipos_inasistencia = cursor.fetchall()
    spf_info_conn.close()
    return render(request, 'horas_procesos/gestion_horas_procesos.html', {
        'form': form,
        'empleados': empleados,
        'procesos': procesos,
        'departamentos': departamentos,
        'rango_procesos': rango_procesos,  # Pasar el rango al contexto
        'productos': productos,
        'tipos_inasistencia': tipos_inasistencia  # Pasar los tipos de inasistencia al contexto
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

        # Obtener los tipos de inasistencia de la base de datos SPF_Info
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
        tipos_inasistencia = cursor.fetchall()
        spf_info_conn.close()

        # Crear un diccionario para mapear ID_Asis a la descripción
        id_a_descripcion = {tipo[0]: tipo[1] for tipo in tipos_inasistencia}

        # Agrupar registros por empleado
        registros_por_empleado = defaultdict(list)
        for registro in registros:
            registros_por_empleado[registro.codigo_emp.codigo_emp].append(registro)

        # Crear una lista de registros combinados
        for codigo_emp, registros in registros_por_empleado.items():
            for registro in registros:
                registro.descripcion_asistencia = id_a_descripcion.get(registro.ID_Asis, '')
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
                proceso.ID_Asis = request.POST.get(f'tipo_inasistencia_{id_hrspro}')  # Actualizar el tipo de inasistencia
                proceso.id_pro = request.POST.get(f'proceso_{id_hrspro}')  # Actualizar el proceso
                proceso.id_producto = request.POST.get(f'producto_{id_hrspro}')  # Actualizar el producto
                proceso.umod = request.user.username  # Guardar el usuario que modificó el registro
                proceso.fmod = date.today()  # Guardar la fecha de modificación
                if proceso.ID_Asis in ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R']:
                    proceso.horaentrada = '00:00:00.0000000'
                    proceso.horasalida = '00:00:00.0000000'
                    proceso.hrs = 0
                    proceso.totalhrs = 0
                    proceso.hrsextras = 0
                    proceso.id_pro = 0
                proceso.save()
                print(f"Updated proceso {id_hrspro}: ID_Asis={proceso.ID_Asis}, horaentrada={proceso.horaentrada}, horasalida={proceso.horasalida}")
            elif key.startswith('eliminar_') and value == 'on':
                eliminar_ids.append(key.split('_')[1])
        
        for id_hrspro in eliminar_ids:
            proceso = Horasprocesos.objects.get(id_hrspro=id_hrspro)
            proceso.delete()
            print(f"Deleted proceso {id_hrspro}")

        messages.success(request, '¡El proceso se actualizó exitosamente!')
        return redirect(reverse('horas_procesos:actualizar_horas_procesos'))
    
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Producto, DescripcionProd FROM Productos")
    productos = cursor.fetchall()
    # Obtener los tipos de inasistencia de la base de datos SPF_Info
    cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
    tipos_inasistencia = cursor.fetchall()
    spf_info_conn.close()
    return render(request, 'horas_procesos/actualizar_horas_procesos.html', {
        'registros_combinados': registros_combinados,
        'departamentos': departamentos,
        'procesos': procesos,
        'departamento_seleccionado': departamento_seleccionado,
        'fecha_seleccionada': fecha_seleccionada,
        'productos': productos,
        'tipos_inasistencia': tipos_inasistencia
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
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, Border, Side


def exportar_a_excel(registros_combinados):
    from openpyxl.styles import PatternFill
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Horas Procesos"

    # Estilos
    header_font = Font(bold=True)
    header_alignment = Alignment(horizontal="center", vertical="center")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    gray_fill = PatternFill(start_color="DDDDDD", end_color="DDDDDD", fill_type="solid")

    # Escribir encabezados
    headers = [
        "Código Emp", "Empleado", "Departamento", "Proceso", "Fecha",
        "Hora Entrada", "Hora Salida", "Horas", "Total Horas", "Horas Extras",
        "Inasistencia", "Creado Por", "Modificado Por", "F/Modificación"
    ]
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        cell = ws[f'{col_letter}1']
        cell.value = header
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
        cell.fill = gray_fill  # Fondo gris para los encabezados

    # Escribir datos
    row_num = 2
    for registro in registros_combinados:
        empleado_empezado = False  # Para manejar espacios visuales
        
        for proceso in registro['procesos']:
            if not empleado_empezado:
                # Escribir datos del empleado en la primera fila
                ws[f'A{row_num}'] = registro['codigo_emp']
                ws[f'B{row_num}'] = registro['nombre_emp']
                ws[f'C{row_num}'] = registro['depto_emp']
                empleado_empezado = True
            
            # Escribir datos del proceso
            ws[f'D{row_num}'] = proceso.id_pro
            ws[f'E{row_num}'] = proceso.fecha_hrspro
            ws[f'F{row_num}'] = proceso.horaentrada
            ws[f'G{row_num}'] = proceso.horasalida
            ws[f'H{row_num}'] = proceso.hrs
            ws[f'I{row_num}'] = proceso.totalhrs
            ws[f'J{row_num}'] = proceso.hrsextras
            ws[f'K{row_num}'] = proceso.asistencia
            ws[f'L{row_num}'] = proceso.ucreado
            ws[f'M{row_num}'] = proceso.umod if proceso.umod else 'N/M'
            ws[f'N{row_num}'] = proceso.fmod if proceso.fmod else 'N/M'

            # Aplicar bordes a las celdas
            for col_num in range(1, len(headers) + 1):
                col_letter = get_column_letter(col_num)
                cell = ws[f'{col_letter}{row_num}']
                cell.border = thin_border
            row_num += 1

    # Resumen al final
    ws[f'H{row_num}'] = "Total Horas:"
    ws[f'I{row_num}'] = f'=SUM(I2:I{row_num - 1})'  # Fórmula para sumar total horas
    ws[f'H{row_num}'].font = header_font
    ws[f'H{row_num}'].alignment = header_alignment

    # Ajustar ancho de columnas
    for col_num in range(1, len(headers) + 1):
        col_letter = get_column_letter(col_num)
        ws.column_dimensions[col_letter].width = 15

    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=horas_procesos.xlsx'
    wb.save(response)
    return response
