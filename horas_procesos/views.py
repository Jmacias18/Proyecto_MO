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
from django.core.cache import cache

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

# Conexión a la base de datos TempusAccesos
tempus_accesos_conn_info = {
    'driver': '{ODBC Driver 17 for SQL Server}',
    'server': 'localhost\\SQLEXPRESS',
    'database': 'TempusAccesos',
    'trusted_connection': 'yes'
}

def get_tempus_accesos_connection():
    return pyodbc.connect(
        driver=tempus_accesos_conn_info['driver'],
        server=tempus_accesos_conn_info['server'],
        database=tempus_accesos_conn_info['database'],
        trusted_connection=tempus_accesos_conn_info['trusted_connection']
    )

import locale
from datetime import datetime

# Establecer la configuración regional a español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def obtener_datos_tempus_accesos():
    conn = get_tempus_accesos_connection()
    cursor = conn.cursor()

    # Obtener los datos de la tabla USERINFO
    cursor.execute("SELECT USERID, Badgenumber FROM USERINFO WHERE Badgenumber LIKE '13%'")
    userinfo = cursor.fetchall()

    # Crear un diccionario para mapear USERID a Badgenumber
    userid_to_badgenumber = {row.USERID: str(row.Badgenumber).strip() for row in userinfo}
    

    # Obtener los datos de la tabla CHECKINOUT
    cursor.execute("SELECT USERID, CHECKTIME FROM CHECKINOUT WHERE CAST(CHECKTIME AS DATE) = CAST(GETDATE() AS DATE)")
    checkinout = cursor.fetchall()

    # Crear un diccionario para almacenar los registros de entrada de hoy
    registros_entrada = {}
    for row in checkinout:
        if row.USERID in userid_to_badgenumber:
            badgenumber = userid_to_badgenumber[row.USERID]
            # Eliminar el prefijo '130' si está presente
            if badgenumber.startswith('130'):
                badgenumber = badgenumber[3:]
            # Mantener solo los últimos 4 dígitos
            badgenumber = badgenumber[-4:]
            registros_entrada[badgenumber] = row.CHECKTIME

    

    conn.close()
    return registros_entrada

def gestion_horas_procesos(request):
    dia_actual = datetime.now().strftime('%A').capitalize()  # Definir dia_actual en ambos métodos
    

    if request.method == 'POST':
        tipos_inasistencia = cache.get('tipos_inasistencia')
        if not tipos_inasistencia:
            spf_info_conn = get_spf_info_connection()
            cursor = spf_info_conn.cursor()
            cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
            tipos_inasistencia = cursor.fetchall()
            spf_info_conn.close()
            cache.set('tipos_inasistencia', tipos_inasistencia, 3600)  # Cachear por 1 hora

        # Crear un diccionario para mapear la descripción al ID_Asis
        descripcion_a_id = {tipo[1]: tipo[0] for tipo in tipos_inasistencia}

        turnos = cache.get('turnos')
        if not turnos:
            spf_info_conn = get_spf_info_connection()
            cursor = spf_info_conn.cursor()
            cursor.execute("SELECT ID_Turno, Descanso FROM Turnos")
            turnos = cursor.fetchall()
            spf_info_conn.close()
            cache.set('turnos', turnos, 3600)  # Cachear por 1 hora

        # Crear un diccionario para mapear el ID del turno a los días de descanso
        descanso_por_turno = {turno[0]: [dia.strip().capitalize() for dia in turno[1].split('/')] if turno[1] else [] for turno in turnos}
        

        # Obtener los ID_Asis para los diferentes tipos de inasistencia
        id_asistencia = descripcion_a_id.get('ASISTENCIA')
        id_descanso = descripcion_a_id.get('DESCANSO')
        id_falta = descripcion_a_id.get('FALTA')
        id_permiso = descripcion_a_id.get('PERMISO')
        id_vacaciones = descripcion_a_id.get('VACACIONES')
        id_incapacidad = descripcion_a_id.get('INCAPACIDAD')
        id_suspension = descripcion_a_id.get('SUSPENCION')
        id_baja = descripcion_a_id.get('BAJA')
        id_renuncia = descripcion_a_id.get('RENUNCIA')
        id_nuevo_ingreso = descripcion_a_id.get('NUEVO INGRESO')
        id_retardo = descripcion_a_id.get('RETARDO')

        # Crear un diccionario para mapear los tipos de inasistencia a sus respectivos IDs y mensajes
        inasistencia_map = {
            'ASI': (id_asistencia, 'ASISTENCIA'),
            'D': (id_descanso, 'DESCANSO'),
            'P': (id_permiso, 'PERMISO'),
            'V': (id_vacaciones, 'VACACIONES'),
            'INC': (id_incapacidad, 'INCAPACIDAD'),
            'S': (id_suspension, 'SUSPENCION'),
            'B': (id_baja, 'BAJA'),
            'R': (id_renuncia, 'RENUNCIA'),
            'NI': (id_nuevo_ingreso, 'NUEVO INGRESO'),
            'RT': (id_retardo, 'RETARDO')
        }

        # Obtener los datos de TempusAccesos
        registros_entrada = obtener_datos_tempus_accesos()
        

        # Filtrar empleados por departamento seleccionado
        departamento_seleccionado = request.POST.get('departamento')
        empleados = Empleados.objects.filter(id_departamento=departamento_seleccionado)

        for empleado in empleados:
            codigo_emp = str(empleado.codigo_emp).strip()[-4:]  # Convertir a string y mantener solo los últimos 4 dígitos
            

            es_descanso = dia_actual in descanso_por_turno.get(str(empleado.id_turno), [])
            

            # Verificar si el empleado tiene una checada registrada
            tiene_checada = codigo_emp in registros_entrada
            

            # Obtener el tipo de inasistencia seleccionado en el formulario
            tipo_inasistencia_seleccionado = request.POST.get(f'tipo_inasistencia_{codigo_emp}', 'F')

            # Determinar el tipo de inasistencia basado en las checadas y el día de descanso
            if tiene_checada:
                tipo_inasistencia = tipo_inasistencia_seleccionado if tipo_inasistencia_seleccionado != 'F' else 'ASI'
            elif es_descanso:
                tipo_inasistencia = 'D'
            else:
                tipo_inasistencia = tipo_inasistencia_seleccionado

            # Asignar el ID_Asis y el mensaje correspondiente
            ID_Asis, mensaje = inasistencia_map.get(tipo_inasistencia, (id_falta, 'FALTA'))
            inasistencia = tipo_inasistencia in ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R']
            

            try:
                if inasistencia:
                    # Insertar un solo registro con valores en cero para empleados con falta o inasistencia similar
                    Horasprocesos.objects.create(
                        fecha_hrspro=timezone.now().date(),
                        codigo_emp=empleado,
                        ID_Asis=ID_Asis,
                        id_pro=0,
                        id_producto=None,
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
                    # Insertar registros de horas de procesos solo si no es inasistencia
                    for i in range(1, 16):
                        id_proceso = request.POST.get(f'proceso{i}_header')
                        hora_entrada = request.POST.get(f'inicio_proceso{i}_{codigo_emp}') or None
                        hora_salida = request.POST.get(f'fin_proceso{i}_{codigo_emp}') or None
                        id_producto = request.POST.get(f'producto{i}_header')
                        horas_extras = request.POST.get(f'horas_extras_{codigo_emp}', 0)

                        if id_proceso and hora_entrada and hora_salida:
                            # Calcular las horas trabajadas
                            formato = '%H:%M'
                            hora_entrada_dt = datetime.strptime(hora_entrada, formato)
                            hora_salida_dt = datetime.strptime(hora_salida, formato)
                            diferencia = hora_salida_dt - hora_entrada_dt
                            horas_trabajadas = diferencia.total_seconds() / 3600

                            # Convertir horas_extras a float
                            horas_extras = float(horas_extras)

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
                            
            except Exception as e:
                print(f"Error al crear registro para empleado {codigo_emp}: {e}")

        
        messages.success(request, '¡Las horas de los procesos se registraron exitosamente!')    
        return redirect('horas_procesos:gestion_horas_procesos')
    else:
        form = HorasProcesosForm()
    
    # Filtrar empleados por departamento seleccionado
    departamento_seleccionado = request.GET.get('departamento')
    if departamento_seleccionado:
        empleados = Empleados.objects.filter(id_departamento=departamento_seleccionado)
    else:
        empleados = Empleados.objects.filter(id_departamento__in=[12, 16, 17, 18, 19, 20, 21, 22, 23])

    procesos = Procesos.objects.filter(estado_pro=True)  # Filtrar solo los procesos activos
    departamentos = Empleados.objects.values_list('id_departamento', flat=True).distinct()
    rango_procesos = range(1, 16)  # Generar el rango de números del 1 al 16

    productos = cache.get('productos')
    if not productos:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Producto, DescripcionProd FROM Productos")
        productos = cursor.fetchall()
        spf_info_conn.close()
        cache.set('productos', productos, 3600)  # Cachear por 1 hora

    tipos_inasistencia = cache.get('tipos_inasistencia')
    if not tipos_inasistencia:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
        tipos_inasistencia = cursor.fetchall()
        spf_info_conn.close()
        cache.set('tipos_inasistencia', tipos_inasistencia, 3600)  # Cachear por 1 hora

    # Crear un diccionario para mapear la descripción al ID_Asis
    descripcion_a_id = {tipo[1]: tipo[0] for tipo in tipos_inasistencia}

    turnos = cache.get('turnos')
    if not turnos:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Turno, Descanso FROM Turnos")
        turnos = cursor.fetchall()
        spf_info_conn.close()
        cache.set('turnos', turnos, 3600)  # Cachear por 1 hora

    # Crear un diccionario para mapear el ID del turno a los días de descanso
    descanso_por_turno = {turno[0]: [dia.strip().capitalize() for dia in turno[1].split('/')] if turno[1] else [] for turno in turnos}
    

    # Obtener la descripción de los departamentos
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos")
    departamentos = cursor.fetchall()
    spf_info_conn.close()

    # Convertir departamentos a un diccionario
    departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

    # Obtener los ID_Asis para ASISTENCIA y DESCANSO
    id_asistencia = descripcion_a_id.get('ASISTENCIA')
    id_descanso = descripcion_a_id.get('DESCANSO')

    # Obtener los datos de TempusAccesos
    registros_entrada = obtener_datos_tempus_accesos()

    # Añadir la descripción del departamento a cada empleado
    empleados_con_descripcion = []
    for empleado in empleados:
        codigo_emp = str(empleado.codigo_emp).strip()[-4:]  # Convertir a string y mantener solo los últimos 4 dígitos
        es_descanso = dia_actual in descanso_por_turno.get(str(empleado.id_turno), [])
        tipo_inasistencia = 'F' if codigo_emp not in registros_entrada else 'ASI'
        
        # Priorizar la checada sobre el día de descanso
        if es_descanso and codigo_emp in registros_entrada:
            tipo_inasistencia = 'ASI'
        elif es_descanso:
            tipo_inasistencia = 'D'
            
        empleado_dict = {
            'codigo_emp': codigo_emp,
            'nombre_emp': empleado.nombre_emp,
            'id_departamento': empleado.id_departamento,
            'descripcion_departamento': departamentos_dict.get(empleado.id_departamento, ''),
            'id_turno': empleado.id_turno,  # Utilizar el campo correcto
            'dias_descanso': descanso_por_turno.get(str(empleado.id_turno), []),  # Obtener los días de descanso
            'es_descanso': es_descanso,  # Verificar si es día de descanso
            'tipo_inasistencia': tipo_inasistencia  # Asignar tipo_inasistencia según el día de descanso y registros de entrada
        }
        empleados_con_descripcion.append(empleado_dict)

    # Lista de IDs de departamentos a mostrar
    departamentos_a_mostrar = [12, 16, 17, 18, 19, 20, 21, 22, 23]

    # Agregar print para ver cómo se pasan los ID_Asis al HTML
    

    return render(request, 'horas_procesos/gestion_horas_procesos.html', {
        'form': form,
        'empleados': empleados_con_descripcion,
        'procesos': procesos,
        'departamentos': [{'id_departamento': depto[0], 'descripcion': depto[1]} for depto in departamentos],
        'rango_procesos': rango_procesos,  # Pasar el rango al contexto
        'productos': productos,
        'tipos_inasistencia': tipos_inasistencia,  # Pasar los tipos de inasistencia al contexto
        'departamentos_a_mostrar': departamentos_a_mostrar  # Pasar la lista de IDs de departamentos a mostrar al contexto
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
    departamentos = []

    # Obtener la descripción de los departamentos
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos")
    departamentos = cursor.fetchall()
    spf_info_conn.close()

    # Filtrar los departamentos con los IDs especificados
    ids_departamentos = [12, 16, 17, 18, 19, 20, 21, 22, 23]
    departamentos = [depto for depto in departamentos if depto[0] in ids_departamentos]
    
    # Convertir departamentos a un diccionario
    departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

    if departamento_seleccionado or fecha_seleccionada:
        registros = Horasprocesos.objects.all()
        empleados = Empleados.objects.all()
        empleados_dict = {empleado.codigo_emp: empleado.id_departamento for empleado in empleados}

        if departamento_seleccionado and departamento_seleccionado != "":
            empleados = empleados.filter(id_departamento=departamento_seleccionado)
            registros = registros.filter(codigo_emp__id_departamento=departamento_seleccionado)
        
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
                'depto_emp': departamentos_dict.get(empleados_dict[codigo_emp], ''),
                'procesos': registros
            }
            registros_combinados.append(registro_combinado)

    # Convertir departamentos a un formato adecuado para el contexto
    departamentos_context = [{'id_departamento': depto[0], 'descripcion': depto[1]} for depto in departamentos]

    procesos = Procesos.objects.all()

    if request.method == 'POST':
        eliminar_ids = []
        for key, value in request.POST.items():
            if key.startswith('horaentrada_'):
                id_hrspro = key.split('_')[1]
                try:
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
                   
                except Horasprocesos.DoesNotExist:
                    messages.error(request, f'El proceso con ID {id_hrspro} no existe.')
            elif key.startswith('eliminar_') and value == 'on':
                eliminar_ids.append(key.split('_')[1])
        
        for id_hrspro in eliminar_ids:
            try:
                proceso = Horasprocesos.objects.get(id_hrspro=id_hrspro)
                proceso.delete()
                
            except Horasprocesos.DoesNotExist:
                messages.error(request, f'El proceso con ID {id_hrspro} no existe.')

        messages.success(request, '¡El proceso se actualizó exitosamente!')
        return redirect(reverse('horas_procesos:actualizar_horas_procesos'))
    
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Producto, DescripcionProd FROM Productos")
    productos = cursor.fetchall()
    
    cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
    tipos_inasistencia = cursor.fetchall()
    spf_info_conn.close()
    
    return render(request, 'horas_procesos/actualizar_horas_procesos.html', {
        'registros_combinados': registros_combinados,
        'departamentos': departamentos_context,
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
