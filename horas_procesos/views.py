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
from django.db.models import Q 

from babel.dates import format_date

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

def obtener_datos_tempus_accesos(fecha):
    conn = get_tempus_accesos_connection()
    cursor = conn.cursor()

    # Obtener los datos de la tabla USERINFO
    cursor.execute("SELECT USERID, Badgenumber FROM USERINFO WHERE Badgenumber LIKE '13%'")
    userinfo = cursor.fetchall()

    # Crear un diccionario para mapear USERID a Badgenumber
    userid_to_badgenumber = {row.USERID: str(row.Badgenumber).strip() for row in userinfo}

    # Obtener los datos de la tabla CHECKINOUT para la fecha seleccionada
    cursor.execute("SELECT USERID, CHECKTIME FROM CHECKINOUT WHERE CAST(CHECKTIME AS DATE) = ?", fecha)
    checkinout = cursor.fetchall()

    # Crear un diccionario para almacenar los registros de entrada de la fecha seleccionada
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
    # Diccionario de traducción de días de la semana de español con acentos a sin acentos
    dias_semana_sin_acentos = {
        'lunes': 'Lunes',
        'martes': 'Martes',
        'miércoles': 'Miercoles',
        'jueves': 'Jueves',
        'viernes': 'Viernes',
        'sábado': 'Sabado',
        'domingo': 'Domingo'
    }

    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Formatear y mostrar el día actual en español usando babel
    dia_actual_con_acento = format_date(fecha_actual, 'EEEE', locale='es_ES').lower()

    # Traducir el día de la semana a sin acentos
    dia_actual_sin_acento = dias_semana_sin_acentos[dia_actual_con_acento]

    empleados_con_descripcion = []
    descanso_por_turno = {}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        fecha_seleccionada = request.GET.get('fecha')
        departamento_seleccionado = request.GET.get('departamento')

        print(f"Fecha seleccionada (AJAX): {fecha_seleccionada}")  # Agregar print de la fecha seleccionada

        if fecha_seleccionada:
            fecha_seleccionada = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()
        else:
            fecha_seleccionada = timezone.now().date()

        registros_entrada = obtener_datos_tempus_accesos(fecha_seleccionada)
        empleados = Empleados.objects.filter(id_departamento=departamento_seleccionado)

        # Obtener la descripción de los departamentos
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos")
        departamentos = cursor.fetchall()
        spf_info_conn.close()

        # Convertir departamentos a un diccionario
        departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

        turnos = cache.get('turnos')
        if not turnos:
            spf_info_conn = get_spf_info_connection()
            cursor = spf_info_conn.cursor()
            cursor.execute("SELECT ID_Turno, Nombre, Horario, Descanso FROM Turnos")
            turnos = cursor.fetchall()
            spf_info_conn.close()
            cache.set('turnos', turnos, 3600)  # Cachear por 1 hora

        # Crear un diccionario para mapear el ID del turno a los días de descanso
        descanso_por_turno = {turno[0]: [dia.strip().capitalize() for dia in turno[3].split('/')] if turno[3] else [] for turno in turnos}

        empleados_con_descripcion = [
            {
                'codigo_emp': emp.codigo_emp,
                'nombre_emp': emp.nombre_emp,
                'id_departamento': emp.id_departamento,
                'descripcion_departamento': departamentos_dict.get(emp.id_departamento, ''),
                'id_turno': emp.id_turno,
                'dias_descanso': descanso_por_turno.get(str(emp.id_turno), []),
                'es_descanso': dia_actual_sin_acento in descanso_por_turno.get(str(emp.id_turno), []),
                'tipo_inasistencia': 'ASI' if emp.codigo_emp in registros_entrada else 'D' if dia_actual_sin_acento in descanso_por_turno.get(str(emp.id_turno), []) else 'F'
            }
            for emp in empleados
        ]

        tipos_inasistencia = cache.get('tipos_inasistencia')
        if not tipos_inasistencia:
            spf_info_conn = get_spf_info_connection()
            cursor = spf_info_conn.cursor()
            cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
            tipos_inasistencia = cursor.fetchall()
            spf_info_conn.close()
            cache.set('tipos_inasistencia', tipos_inasistencia, 3600)  # Cachear por 1 hora

        return JsonResponse({
            'empleados': empleados_con_descripcion,
            'tipos_inasistencia': [{'ID_Asis': tipo[0], 'Descripcion': tipo[1]} for tipo in tipos_inasistencia],
            'turnos': [{'id': turno[0], 'nombre': turno[1], 'horario': turno[2], 'descanso': turno[3]} for turno in turnos]
        })

    if request.method == 'POST':
        # Obtener la fecha seleccionada del formulario
        fecha_seleccionada = request.POST.get('fecha')
        print(f"Fecha seleccionada (POST): {fecha_seleccionada}")  # Agregar print de la fecha seleccionada

        if not fecha_seleccionada:
            fecha_seleccionada = timezone.now().date()  # Usar la fecha actual si no se selecciona ninguna
        else:
            fecha_seleccionada = datetime.strptime(fecha_seleccionada, '%Y-%m-%d').date()

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
        registros_entrada = obtener_datos_tempus_accesos(fecha_seleccionada)

        # Filtrar empleados por departamento seleccionado
        departamento_seleccionado = request.POST.get('departamento')
        empleados = Empleados.objects.filter(id_departamento=departamento_seleccionado)

        # Obtener la descripción de los departamentos
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos")
        departamentos = cursor.fetchall()
        spf_info_conn.close()

        # Convertir departamentos a un diccionario
        departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

        for empleado in empleados:
            codigo_emp = str(empleado.codigo_emp).strip()[-4:]  # Convertir a string y mantener solo los últimos 4 dígitos

            es_descanso = dia_actual_sin_acento in descanso_por_turno.get(str(empleado.id_turno), [])

            # Verificar si el empleado tiene una checada registrada
            tiene_checada = codigo_emp in registros_entrada

            # Determinar el tipo de inasistencia basado en las checadas y el día de descanso
            if tiene_checada:
                tipo_inasistencia = 'ASI'
            elif es_descanso:
                tipo_inasistencia = 'D'
            else:
                tipo_inasistencia = 'F'

            # Verificar si hay un tipo de inasistencia seleccionado en el formulario
            tipo_inasistencia_form = request.POST.get(f'tipo_inasistencia_{codigo_emp}')
            if tipo_inasistencia_form:
                tipo_inasistencia = tipo_inasistencia_form

            # Asignar el ID_Asis y el mensaje correspondiente
            ID_Asis, mensaje = inasistencia_map.get(tipo_inasistencia, (id_falta, 'FALTA'))
            inasistencia = tipo_inasistencia in ['F', 'D', 'P', 'V', 'INC', 'S', 'B', 'R']

            empleados_con_descripcion.append({
                'codigo_emp': empleado.codigo_emp,
                'nombre_emp': empleado.nombre_emp,
                'id_departamento': empleado.id_departamento,
                'descripcion_departamento': departamentos_dict.get(empleado.id_departamento, ''),
                'id_turno': empleado.id_turno,
                'dias_descanso': descanso_por_turno.get(str(empleado.id_turno), []),
                'es_descanso': es_descanso,
                'tipo_inasistencia': tipo_inasistencia
            })

            try:
                if inasistencia:
                    # Insertar un solo registro con valores en cero para empleados con falta o inasistencia similar
                    Horasprocesos.objects.create(
                        fecha_hrspro=fecha_seleccionada,
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
                        fmod=None,
                        hrcomida=False
                    )
                else:
                    # Insertar registros de horas de procesos solo si no es inasistencia
                    horas_extras = request.POST.get(f'horas_extras_{codigo_emp}', 0)
                    horas_extras_asignadas = False  # Variable para controlar la asignación de horas extras
                    for i in range(1, 11):
                        id_proceso = request.POST.get(f'proceso{i}_header')
                        hora_entrada = request.POST.get(f'inicio_proceso{i}_{codigo_emp}') or None
                        hora_salida = request.POST.get(f'fin_proceso{i}_{codigo_emp}') or None
                        id_producto = request.POST.get(f'producto{i}_header')
                        hrs = request.POST.get(f'total_proceso{i}_{codigo_emp}', 0)
                        hrcomida = request.POST.get(f'comida_proceso{i}_{codigo_emp}', 'off') == 'on'  # Obtener el valor del checkbox de comida

                        if id_proceso and hora_entrada and hora_salida:
                            # Calcular las horas trabajadas
                            formato = '%H:%M'
                            hora_entrada_dt = datetime.strptime(hora_entrada, formato)
                            hora_salida_dt = datetime.strptime(hora_salida, formato)
                            diferencia = hora_salida_dt - hora_entrada_dt
                            horas_trabajadas = diferencia.total_seconds() / 3600

                            # Asignar horas extras solo al primer proceso
                            if not horas_extras_asignadas:
                                try:
                                    horas_extras = float(horas_extras)
                                except ValueError:
                                    horas_extras = 0.0
                                horas_extras_asignadas = True
                                # No sumar horas extras a hrs y totalhrs
                                total_hrs = horas_trabajadas
                            else:
                                horas_extras = 0.0
                                total_hrs = horas_trabajadas

                            try:
                                hrs = float(hrs)
                            except ValueError:
                                hrs = 0.0

                            Horasprocesos.objects.create(
                                fecha_hrspro=fecha_seleccionada,
                                codigo_emp=empleado,
                                ID_Asis=ID_Asis,
                                id_pro=id_proceso,
                                id_producto=id_producto,
                                horaentrada=hora_entrada,
                                horasalida=hora_salida,
                                hrs=hrs,
                                totalhrs=total_hrs,
                                hrsextras=horas_extras,
                                autorizado=False,
                                sync=False,
                                ucreado=request.user.username,  # Guardar el usuario que creó el registro
                                umod=None,  # Guardar el usuario que modificó el registro
                                fmod=None,
                                hrcomida=hrcomida  # Guardar el valor del checkbox de comida
                            )
            except Exception as e:
                print(f"Error al crear registro para empleado {codigo_emp}: {e}")

        messages.success(request, '¡Las horas de los procesos se registraron exitosamente!')
        return redirect('horas_procesos:gestion_horas_procesos')
    else:
        form = HorasProcesosForm()

    # Obtener la descripción de los departamentos
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos WHERE ID_Departamento IN (12, 16, 17, 18, 19, 20, 21, 22, 23)")
    departamentos = cursor.fetchall()

    """ # Obtener los productos
    cursor.execute("SELECT ID_Producto, DescripcionProd FROM Productos")
    productos = cursor.fetchall() """
    
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("""
        SELECT p.ID_Producto, p.DescripcionProd, COALESCE(c.Cliente, 'Sin Cliente') as Cliente
        FROM Productos p
        LEFT JOIN Clientes c ON p.ID_Cliente = c.ID_Cliente
        WHERE p.ID_Producto LIKE 'PT%' OR p.ID_Producto NOT LIKE '%[^0-9]%'
    """)
    productos = cursor.fetchall()
    spf_info_conn.close()

    # Convertir departamentos a un diccionario
    departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

    tipos_inasistencia = cache.get('tipos_inasistencia')
    if not tipos_inasistencia:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
        tipos_inasistencia = cursor.fetchall()
        spf_info_conn.close()
        cache.set('tipos_inasistencia', tipos_inasistencia, 3600)  # Cachear por 1 hora

    turnos = cache.get('turnos')
    if not turnos:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Turno, Turno, Horario, Descanso FROM Turnos")
        turnos = cursor.fetchall()
        spf_info_conn.close()
        cache.set('turnos', turnos, 3600)  # Cachear por 1 hora

    # Crear un diccionario para mapear el ID del turno a los días de descanso
    descanso_por_turno = {}
    for turno in turnos:
        # Verificar que el turno tenga al menos 4 elementos y que el cuarto elemento sea una cadena
        if len(turno) > 3 and isinstance(turno[3], str):
            # Dividir la cadena de días de descanso y capitalizar cada día
            descanso_por_turno[turno[0]] = [dia.strip().capitalize() for dia in turno[3].split('/')]
        else:
            # Si no tiene al menos 4 elementos o el cuarto elemento no es una cadena, asignar una lista vacía
            descanso_por_turno[turno[0]] = []

    """ print(f"Descanso por turno: {descanso_por_turno}") """
    # Obtener los datos de TempusAccesos
    registros_entrada = obtener_datos_tempus_accesos(fecha_actual.date())

    procesos = Procesos.objects.filter(estado_pro=True)  # Filtrar solo los procesos activos
    rango_procesos = range(1, 11)  # Generar el rango de números del 1 al 11

    return render(request, 'horas_procesos/gestion_horas_procesos.html', {
        'form': form,
        'empleados': empleados_con_descripcion,
        'procesos': procesos,
        'departamentos': [{'id_departamento': depto[0], 'descripcion': depto[1]} for depto in departamentos],
        'rango_procesos': rango_procesos,  # Pasar el rango al contexto
        'productos': productos,
        'tipos_inasistencia': tipos_inasistencia,  # Pasar los tipos de inasistencia al contexto
        'turnos': [{'id': turno[0], 'nombre': turno[1], 'horario': turno[2], 'descanso': turno[3]} for turno in turnos],  # Pasar los turnos al contexto
        'departamentos_a_mostrar': [12, 16, 17, 18, 19, 20, 21, 22, 23],  # Pasar la lista de IDs de departamentos a mostrar al contexto
        'empleados_motivo': list(Motivo.objects.values_list('codigo_emp', flat=True))  # Pasar la lista de empleados de la tabla Motivo al contexto
    })


def obtener_primera_checada(fecha):
    conn = get_tempus_accesos_connection()
    cursor = conn.cursor()

    # Obtener los datos de la tabla USERINFO
    cursor.execute("SELECT USERID, Badgenumber FROM USERINFO WHERE Badgenumber LIKE '13%'")
    userinfo = cursor.fetchall()

    # Crear un diccionario para mapear USERID a Badgenumber
    userid_to_badgenumber = {row.USERID: str(row.Badgenumber).strip() for row in userinfo}

    # Obtener los datos de la tabla CHECKINOUT para la fecha seleccionada
    cursor.execute("SELECT USERID, MIN(CHECKTIME) as CHECKTIME FROM CHECKINOUT WHERE CAST(CHECKTIME AS DATE) = ? GROUP BY USERID", fecha)
    checkinout = cursor.fetchall()

    # Crear un diccionario para almacenar los registros de entrada de la fecha seleccionada
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

def obtener_ultima_checada(fecha):
    conn = get_tempus_accesos_connection()
    cursor = conn.cursor()

    # Obtener los datos de la tabla USERINFO
    cursor.execute("SELECT USERID, Badgenumber FROM USERINFO WHERE Badgenumber LIKE '13%'")
    userinfo = cursor.fetchall()

    # Crear un diccionario para mapear USERID a Badgenumber
    userid_to_badgenumber = {row.USERID: str(row.Badgenumber).strip() for row in userinfo}

    # Obtener los datos de la tabla CHECKINOUT para la fecha seleccionada
    cursor.execute("SELECT USERID, MAX(CHECKTIME) as CHECKTIME FROM CHECKINOUT WHERE CAST(CHECKTIME AS DATE) = ? GROUP BY USERID", fecha)
    checkinout = cursor.fetchall()

    # Crear un diccionario para almacenar los registros de salida de la fecha seleccionada
    registros_salida = {}
    for row in checkinout:
        if row.USERID in userid_to_badgenumber:
            badgenumber = userid_to_badgenumber[row.USERID]
            # Eliminar el prefijo '130' si está presente
            if badgenumber.startswith('130'):
                badgenumber = badgenumber[3:]
            # Mantener solo los últimos 4 dígitos
            badgenumber = badgenumber[-4:]
            registros_salida[badgenumber] = row.CHECKTIME

    conn.close()
    return registros_salida


def empleados_por_departamento(request):
    departamento_id = request.GET.get('departamento', None)
    search_query = request.GET.get('search', '')
    fecha_filtro = request.GET.get('fecha', datetime.now().date().strftime('%Y-%m-%d'))
    fecha_filtro = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
    empleados = Empleados.objects.none()
    total_empleados = 0

    if departamento_id:
        empleados = Empleados.objects.filter(id_departamento=departamento_id)
        total_empleados = empleados.count()

    if search_query:
        empleados = empleados.filter(
            Q(codigo_emp__icontains=search_query) |
            Q(nombre_emp__icontains=search_query)
        )

    # Obtener la descripción de los departamentos
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos WHERE Descripcion LIKE '%PRODUCCION%'")
    departamentos = cursor.fetchall()
    spf_info_conn.close()

    departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

    # Obtener los datos de TempusAccesos
    registros_entrada = obtener_primera_checada(fecha_filtro)
    registros_salida = obtener_ultima_checada(fecha_filtro)

    # Obtener los turnos y días de descanso
    turnos = cache.get('turnos')
    if not turnos:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Turno, Turno, Horario, Descanso FROM Turnos")
        turnos = cursor.fetchall()
        spf_info_conn.close()
        cache.set('turnos', turnos, 3600)  # Cachear por 1 hora

    turnos_dict = {turno[0]: {'nombre': turno[1], 'horario': turno[2], 'descanso': turno[3]} for turno in turnos}

    # Diccionario de traducción de días de la semana de español con acentos a sin acentos
    dias_semana_sin_acentos = {
        'lunes': 'Lunes',
        'martes': 'Martes',
        'miércoles': 'Miercoles',
        'jueves': 'Jueves',
        'viernes': 'Viernes',
        'sábado': 'Sabado',
        'domingo': 'Domingo'
    }

    # Formatear y mostrar el día actual en español usando babel
    dia_actual_con_acento = format_date(fecha_filtro, 'EEEE', locale='es_ES').lower()
    dia_actual_sin_acento = dias_semana_sin_acentos[dia_actual_con_acento]

    empleados_con_descripcion = [
        {
            'codigo_emp': emp.codigo_emp,
            'nombre_emp': emp.nombre_emp,
            'descripcion_departamento': departamentos_dict.get(emp.id_departamento, ''),
            'tipo_asistencia': 'ASISTENCIA' if str(emp.codigo_emp).strip()[-4:] in registros_entrada else 'DESCANSO' if dia_actual_sin_acento in turnos_dict.get(emp.id_turno, {}).get('descanso', '').split('/') else 'FALTA',
            'hora_entrada': registros_entrada.get(str(emp.codigo_emp).strip()[-4:], '').strftime('%I:%M %p') if str(emp.codigo_emp).strip()[-4:] in registros_entrada else '',
            'hora_salida': registros_salida.get(str(emp.codigo_emp).strip()[-4:], '').strftime('%I:%M %p') if str(emp.codigo_emp).strip()[-4:] in registros_salida else '',
            'turno': turnos_dict.get(emp.id_turno, {}).get('nombre', ''),
            'horario': turnos_dict.get(emp.id_turno, {}).get('horario', ''),
            'descanso': turnos_dict.get(emp.id_turno, {}).get('descanso', '')
        }
        for emp in empleados
    ]

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'empleados': empleados_con_descripcion})

    return render(request, 'horas_procesos/empleados_por_departamento.html', {
        'empleados': empleados_con_descripcion,
        'departamentos': [{'id_departamento': depto[0], 'descripcion': depto[1]} for depto in departamentos],
        'total_empleados': total_empleados,
        'search_query': search_query,
        'fecha_filtro': fecha_filtro.strftime('%Y-%m-%d')
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
def display_employees(request):
    codigo_emp = request.GET.get('codigo_emp', '')
    nombre_emp = request.GET.get('nombre_emp', '')
    departamento = request.GET.get('departamento', '')

    empleados = Empleados.objects.none()  # No cargar empleados inicialmente

    # Obtener la descripción de los departamentos
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT ID_Departamento, Descripcion FROM Departamentos WHERE ID_Departamento IN (12, 16, 17, 18, 19, 20, 21, 22, 23)")
    departamentos = cursor.fetchall()
    spf_info_conn.close()

    departamentos_dict = {depto[0]: depto[1] for depto in departamentos}

    if codigo_emp or nombre_emp or departamento:
        empleados = Empleados.objects.all()
        if codigo_emp:
            empleados = empleados.filter(codigo_emp__icontains=codigo_emp)
        if nombre_emp:
            empleados = empleados.filter(nombre_emp__icontains=nombre_emp)
        if departamento:
            empleados = empleados.filter(id_departamento=departamento)

        empleados_con_descripcion = []
        for empleado in empleados:
            empleado_dict = {
                'codigo_emp': empleado.codigo_emp,
                'nombre_emp': empleado.nombre_emp,
                'descripcion_departamento': departamentos_dict.get(empleado.id_departamento, ''),
                'sync': False,  # Valor por defecto
                'estado': 'Pendiente'  # Valor por defecto
            }
            empleados_con_descripcion.append(empleado_dict)
    else:
        empleados_con_descripcion = []

    # Obtener los empleados de la tabla Motivo
    empleados_motivo = Motivo.objects.all()

    # Añadir la descripción del departamento a los motivos
    for motivo in empleados_motivo:
        motivo.descripcion_departamento = departamentos_dict.get(int(motivo.departamento), '')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'empleados': empleados_con_descripcion})

    return render(request, 'horas_procesos/display_employees.html', {
        'empleados': empleados_con_descripcion,
        'departamentos': [{'id_departamento': depto[0], 'descripcion': depto[1]} for depto in departamentos],
        'empleados_motivo': empleados_motivo
    })

def eliminar_motivo(request, id):
    motivo = get_object_or_404(Motivo, id=id)
    motivo.delete()
    return redirect('horas_procesos:display_employees')

def actualizar_motivo(request, id):
    motivo = get_object_or_404(Motivo, id=id)
    
    # Obtener la descripción del departamento
    spf_info_conn = get_spf_info_connection()
    cursor = spf_info_conn.cursor()
    cursor.execute("SELECT Descripcion FROM Departamentos WHERE ID_Departamento = ?", [motivo.departamento])
    departamento_descripcion = cursor.fetchone()
    spf_info_conn.close()

    if request.method == 'POST':
        form = MotivoForm(request.POST, instance=motivo)
        if form.is_valid():
            form.save()
            return redirect('horas_procesos:display_employees')
    else:
        form = MotivoForm(instance=motivo)
    
    return render(request, 'horas_procesos/actualizar_motivo.html', {
        'form': form,
        'motivo': motivo,
        'departamento_descripcion': departamento_descripcion[0] if departamento_descripcion else ''
    })
from django.shortcuts import redirect



from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import Motivo, Empleados
from .forms import MotivoForm

def agregar_motivo(request):
    if request.method == 'POST':
        print("Solicitud POST recibida en agregar_motivo")
        for key, value in request.POST.items():
            print(f"Clave: {key}, Valor: {value}")
            if key.startswith('motivo_'):
                codigo_emp = key.split('_')[1]
                motivo = value
                try:
                    empleado = Empleados.objects.get(codigo_emp=codigo_emp)
                    # Guardar el motivo en la base de datos
                    Motivo.objects.create(
                        codigo_emp=codigo_emp,
                        nombre_emp=empleado.nombre_emp,
                        departamento=empleado.id_departamento,
                        motivo=motivo,
                        sync=False,
                        estado=True
                    )
                    print(f'Empleado: {codigo_emp}, Motivo: {motivo}')
                except Empleados.DoesNotExist:
                    print(f'Empleado con código {codigo_emp} no encontrado')
        return redirect('horas_procesos:display_employees')
    print("Solicitud GET recibida en agregar_motivo")
    return redirect('horas_procesos:display_employees')

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
                'id_turno': registros[0].codigo_emp.id_turno,  # Asegúrate de incluir el id_turno
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
                    if proceso.ID_Asis in ['F', 'D', 'V', 'INC', 'S', 'B', 'R']:
                        proceso.horaentrada = '00:00:00.0000000'
                        proceso.horasalida = '00:00:00.0000000'
                        proceso.hrs = 0
                        proceso.totalhrs = 0
                        proceso.hrsextras = 0
                        proceso.id_pro = 0
                    proceso.save()
                except Horasprocesos.DoesNotExist:
                    messages.error(request, f'El proceso con ID {id_hrspro} no existe.')
            elif key.startswith('hrsextras_'):
                id_hrspro = key.split('_')[1]
                try:
                    proceso = Horasprocesos.objects.get(id_hrspro=id_hrspro)
                    proceso.hrsextras = request.POST.get(f'hrsextras_{id_hrspro}')
                    proceso.umod = request.user.username  # Guardar el usuario que modificó el registro
                    proceso.fmod = date.today()  # Guardar la fecha de modificación
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
    cursor.execute("""
        SELECT p.ID_Producto, p.DescripcionProd, COALESCE(c.Cliente, 'Sin Cliente') as Cliente
        FROM Productos p
        LEFT JOIN Clientes c ON p.ID_Cliente = c.ID_Cliente
        WHERE p.ID_Producto LIKE 'PT%' OR p.ID_Producto NOT LIKE '%[^0-9]%'
    """)
    productos = cursor.fetchall()
    
    cursor.execute("SELECT ID_Asis, Descripcion FROM Tipo_Asist")
    tipos_inasistencia = cursor.fetchall()
    spf_info_conn.close()


    # Obtener los turnos
    turnos = cache.get('turnos')
    if not turnos:
        spf_info_conn = get_spf_info_connection()
        cursor = spf_info_conn.cursor()
        cursor.execute("SELECT ID_Turno, Turno, Horario, Descanso FROM Turnos")  # Asegúrate de que las columnas sean correctas
        turnos = cursor.fetchall()
        spf_info_conn.close()
        cache.set('turnos', turnos, 3600)  # Cachear por 1 hora
    
    return render(request, 'horas_procesos/actualizar_horas_procesos.html', {
        'registros_combinados': registros_combinados,
        'departamentos': departamentos_context,
        'procesos': procesos,
        'departamento_seleccionado': departamento_seleccionado,
        'fecha_seleccionada': fecha_seleccionada,
        'productos': productos,
        'tipos_inasistencia': tipos_inasistencia,
        'turnos': [{'id': turno[0], 'nombre': turno[1], 'horario': turno[2], 'descanso': turno[3]} for turno in turnos]  # Pasar los turnos al contexto
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

