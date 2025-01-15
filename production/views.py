from django.shortcuts import render, redirect, get_object_or_404
from django.db import OperationalError
from django.contrib import messages
from .models import ParosProduccion, Procesos, Maquinaria, Productos, Clientes
from .forms import ParosProduccionForm, ProcesosForm, MaquinariaForm, ParoMantForm
from django.contrib.auth.decorators import login_required
import pyodbc
from django.db import ProgrammingError
from datetime import date
from django.urls import reverse


@login_required
def production(request):
    # Obtener los parámetros de los filtros
    hora_inicio = request.GET.get('HoraInicio')
    hora_fin = request.GET.get('HoraFin')
    proceso_id = request.GET.get('ID_Pro')
    maquinaria_id = request.GET.get('ID_Maquinaria')
    fecha_paro = request.GET.get('FechaParo')  # Agregar el filtro por fecha

    # Comprobar si el usuario pertenece al grupo "Mantenimiento"
    user_is_maintenance = request.user.groups.filter(name='Mantenimiento').exists()

    # Lee los paros desde la base de datos 'spf_calidad'
    try:
        paros = ParosProduccion.objects.using('spf_calidad').all()

        # Filtrar por HoraInicio y HoraFin si se proporcionan
        if hora_inicio and hora_fin:
            paros = paros.filter(HoraInicio__gte=hora_inicio, HoraFin__lte=hora_fin)

        # Filtrar por Proceso si se proporciona
        if proceso_id:
            paros = paros.filter(ID_Proceso_id=proceso_id)

        # Filtrar por Maquinaria si se proporciona
        if maquinaria_id:
            paros = paros.filter(ID_Maquinaria_id=maquinaria_id)

        # Filtrar por FechaParo si se proporciona
        if fecha_paro:
            paros = paros.filter(FechaParo=fecha_paro)  # Filtrar por fecha exacta

        # Ordenar los resultados por FechaParo y HoraInicio
        paros = paros.order_by('-FechaParo', '-HoraInicio')

        # Contar los registros no sincronizados (SYNC=False)
        registros_por_syncronizar = ParosProduccion.objects.using('spf_calidad').filter(SYNC=False).count()

    except ProgrammingError:
        paros = []
        registros_por_syncronizar = 0
        messages.error(request, 'Error al acceder a la tabla de ParosProduccion.')

    # Lee los procesos desde la base de datos 'SPF_HRS_MO'
    procesos = Procesos.objects.using('default').filter(Estado_Pro=True)
    maquinarias = Maquinaria.objects.using('spf_info').filter(Estado=True)
    productos = Productos.objects.using('spf_info').all()  # Filtrar productos activos
    clientes = Clientes.objects.all()

    # Crear el contexto con todos los datos necesarios
    context = {
        'paros': paros,
        'procesos': procesos,
        'maquinarias': maquinarias,
        'productos': productos,
        'clientes': clientes,
        'registros_por_syncronizar': registros_por_syncronizar,
        'user_is_maintenance': user_is_maintenance,  # Incluir la variable user_is_maintenance
    }

    # Renderiza la plantilla con el contexto
    return render(request, 'production/production.html', context)


@login_required
def registrar_paro(request):
    if request.method == 'POST':
        form = ParosProduccionForm(request.POST)
        if form.is_valid():
            paro = form.save(commit=False)
            paro.SYNC = False  # Marca como no sincronizado
            paro.save(using='spf_calidad')  # Cambiado a 'spf_calidad'
            messages.success(request, 'Paro registrado exitosamente.')
            return redirect('production:production')
    else:
        form = ParosProduccionForm()

    # Cargar paros desde la base de datos SPF_Calidad
    paros = ParosProduccion.objects.using('spf_calidad').all()  # Cambiado a 'spf_calidad'
    
    procesos = Procesos.objects.using('default').filter(Estado_Pro=1)
    maquinarias = Maquinaria.objects.using('spf_info').filter(Estado=1)
    productos = Productos.objects.using('spf_info').all()  # Filtrar productos activos
    clientes = Clientes.objects.all()  # Cargar todos los clientes (puedes aplicar un filtro si lo deseas)

    return render(request, 'production/production.html', {
        'form': form,
        'paros': paros,
        'procesos': procesos,
        'maquinarias': maquinarias,
        'productos': productos,
        'clientes': clientes, 
    })




@login_required
def modificar_paro(request, paro_id):
    paro = get_object_or_404(ParosProduccion.objects.using('spf_calidad'), ID_Paro=paro_id)

    if request.method == 'POST':
        form = ParosProduccionForm(request.POST, instance=paro)
        if form.is_valid():
            form.save()
            paro.SYNC = False  # Marca como no sincronizado
            paro.save(using='spf_calidad')  # Guarda el cambio en la base de datos SPF_Calidad
            messages.success(request, 'Paro modificado exitosamente. Ahora está marcado como no sincronizado.')
            return redirect('production:production')
    else:
        form = ParosProduccionForm(instance=paro)

    return render(request, 'production/modificar_paro.html', {
        'form': form,
        'paro': paro
    })

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ParoMantForm
from .models import ParosProduccion

@login_required
def modificar_paro_mant(request, paro_id):
    # Obtener el objeto Paro con el ID proporcionado, si no existe devuelve un error 404
    paro = get_object_or_404(ParosProduccion, ID_Paro=paro_id)

    # Verificar si el usuario pertenece al grupo de 'Mantenimiento'
    es_mantenimiento = request.user.groups.filter(name='Mantenimiento').exists()

    if not es_mantenimiento:
        # Redirigir si el usuario no tiene permisos de mantenimiento
        return redirect('production:production')  

    # Procesar el formulario cuando se envíe por POST
    if request.method == 'POST':
        form = ParoMantForm(request.POST, instance=paro)
        if form.is_valid():
            # Marcar como no sincronizado
            paro = form.save(commit=False)
            paro.SYNC = False  # Marca como no sincronizado
            paro.save()

            # Mensaje informando que se necesita sincronización
            messages.info(request, "El paro se ha modificado correctamente, pero aún no está sincronizado. Por favor, sincronícelo para completar el proceso.")

            # Redirigir a la vista de producción después de guardar
            return redirect('production:production')
    else:
        # Si no es un POST, solo se muestra el formulario con los datos actuales
        form = ParoMantForm(instance=paro)

    # Renderizar la página con el formulario y el objeto 'paro'
    return render(request, 'production/modificar_paro_mant.html', {
        'paro': paro,
        'user_is_maintenance': es_mantenimiento,  # Variable para verificar permisos en la plantilla
        'form': form,  # El formulario para modificar el paro
    })



@login_required
def eliminar_paro(request, paro_id):
    paro = get_object_or_404(ParosProduccion.objects.using('spf_calidad'), ID_Paro=paro_id)
    if request.method == 'POST':
        paro.delete(using='spf_calidad')
        messages.success(request, 'Paro eliminado exitosamente.')
        return redirect('production:production')
    return render(request, 'production/eliminar_paro.html', {'paro': paro})




# Registro de procesos y maquinarias
@login_required
def registro(request):
    if request.method == 'POST':
        proceso_form = ProcesosForm(request.POST)
        maquinaria_form = MaquinariaForm(request.POST)

        if proceso_form.is_valid() and maquinaria_form.is_valid():
            # Guarda los datos de proceso y maquinaria
            proceso_form.save()
            maquinaria_form.save()
            messages.success(request, 'Proceso y maquinaria registrados exitosamente.')
            return redirect('production:registro')
    else:
        proceso_form = ProcesosForm()
        maquinaria_form = MaquinariaForm()

    # Inicializa los registros y la cuenta de registros no sincronizados
    registros_proc_por_syncronizar = 0
    registros_maq_por_syncronizar = 0

    try:
        # Contar registros no sincronizados (SYNC=False)
        registros_proc_por_syncronizar = Procesos.objects.using('default').filter(SYNC=False).count()
        registros_maq_por_syncronizar = Maquinaria.objects.using('spf_info').filter(SYNC=False).count()
    except ProgrammingError:
        messages.error(request, 'Error al acceder a las Tablas.')

    # Obtiene todos los procesos y maquinarias existentes
    procesos = Procesos.objects.using('default').all()
    maquinarias = Maquinaria.objects.using('spf_info').all()

    return render(request, 'production/registro.html', {
        'proceso_form': proceso_form,
        'maquinaria_form': maquinaria_form,
        'procesos': procesos,
        'maquinarias': maquinarias,
        'registros_proc_por_syncronizar': registros_proc_por_syncronizar,
        'registros_maq_por_syncronizar': registros_maq_por_syncronizar, # Agregar la cuenta al contexto
    })

@login_required
def registro_proceso(request):
    if request.method == 'POST':
        proceso_form = ProcesosForm(request.POST)
        if proceso_form.is_valid():
            proceso_form.save()
            messages.success(request, 'Proceso registrado exitosamente.')
            return redirect('production:registro_proceso')
    else:
        proceso_form = ProcesosForm()

    # Obtiene todos los procesos existentes
    procesos = Procesos.objects.using('default').all()

    return render(request, 'production/registro_procesos.html', {
        'proceso_form': proceso_form,
        'procesos': procesos,
    })

@login_required
def registro_maquinaria(request):
    if request.method == 'POST':
        maquinaria_form = MaquinariaForm(request.POST)
        if maquinaria_form.is_valid():
            # Crea una instancia de Maquinaria usando el formulario
            maquinaria = maquinaria_form.save(commit=False)
            # Guarda en la base de datos spf_info
            maquinaria.save(using='spf_info')
            messages.success(request, 'Maquinaria registrada exitosamente.')
            return redirect('production:registro_maquinaria')
    else:
        maquinaria_form = MaquinariaForm()

    # Obtiene todas las maquinarias existentes de spf_info
    maquinarias = Maquinaria.objects.using('spf_info').all()

    return render(request, 'production/registro_maquinaria.html', {
        'maquinaria_form': maquinaria_form,
        'maquinarias': maquinarias,
    })



# Modificar un proceso existente
@login_required
def modificar_proceso(request, proceso_id):
    proceso = get_object_or_404(Procesos, ID_Pro=proceso_id)

    if request.method == 'POST':
        form = ProcesosForm(request.POST, instance=proceso)  # Aquí se especifica la instancia
        if form.is_valid():
            proceso.SYNC = False
            form.save()
            messages.success(request, 'Proceso modificado exitosamente.')
            return redirect('production:registro')
    else:
        form = ProcesosForm(instance=proceso)  # Inicializa el formulario con los datos del proceso

    return render(request, 'production/modificar_proceso.html', {
        'form': form,
        'proceso': proceso
    })

# Modificar maquinaria existente
@login_required
def modificar_maquinaria(request, maquinaria_id):
    maquinaria = get_object_or_404(Maquinaria, ID_Maquinaria=maquinaria_id)

    if request.method == 'POST':
        form = MaquinariaForm(request.POST, instance=maquinaria)
        if form.is_valid():
            maquinaria.SYNC = False
            form.save()
            messages.success(request, 'Maquinaria modificada exitosamente.')
            return redirect('production:registro')
    else:
        form = MaquinariaForm(instance=maquinaria)

    return render(request, 'production/modificar_maquinaria.html', {
        'form': form,
        'maquinaria': maquinaria
    })


def cambiar_estado_proceso(request, id_proceso):
    proceso = get_object_or_404(Procesos, ID_Pro=id_proceso)
    proceso.Estado_Pro = not proceso.Estado_Pro  # Cambia el estado
    proceso.SYNC = False  # Indica que se necesita sincronizar
    proceso.save()

    messages.info(request, "El estado del proceso ha sido cambiado. Por favor, sincroniza los datos.")

    return redirect('production:registro')

def cambiar_estado_maquinaria(request, id_maquinaria):
    maquinaria = get_object_or_404(Maquinaria, ID_Maquinaria=id_maquinaria)
    maquinaria.Estado = not maquinaria.Estado  # Cambia el estado
    maquinaria.SYNC = False  # Indica que se necesita sincronizar
    maquinaria.save()

    messages.info(request, "El estado de la maquinaria ha sido cambiado. Por favor, sincroniza los datos.")

    return redirect('production:registro')


@login_required
def sync_data_view(request):
    # Obtener registros no sincronizados de la base de datos local
    registros_no_sync = ParosProduccion.objects.using('spf_calidad').filter(SYNC=False)

    # Cadena de conexión al servidor
    server_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=QBSERVER\\SQLEXPRESS;"
        "Database=SPF_Calidad;"
        "UID=it;"
        "PWD=sqlSPF#2024;"
    )

    try:
        with pyodbc.connect(server_conn_str) as conn:
            cursor = conn.cursor()

            for registro in registros_no_sync:
                if getattr(registro, 'DELETED', False):
                    cursor.execute("DELETE FROM ParosProduccion WHERE ID_Paro = ?", (registro.ID_Paro,))
                else:
                    id_cliente = registro.ID_Cliente_id if registro.ID_Cliente is not None else None
                    orden_fabricacion = registro.OrdenFabricacionSAP if registro.OrdenFabricacionSAP is not None else 0
                    id_producto = registro.ID_Producto if registro.ID_Producto is not None else ''
                    fecha_paro = registro.FechaParo if registro.FechaParo is not None else date.today()
                    hora_inicio = registro.HoraInicio if registro.HoraInicio is not None else '00:00:00'
                    hora_fin = registro.HoraFin if registro.HoraFin is not None else '00:00:00'
                    tiempo_muerto = registro.TiempoMuerto if registro.TiempoMuerto is not None else 0
                    personas_afectadas = registro.PersonasAfectadas if registro.PersonasAfectadas is not None else 0
                    mo = registro.MO if registro.MO is not None else 0
                    id_proceso = registro.ID_Proceso_id if registro.ID_Proceso is not None else None
                    id_maquinaria = registro.ID_Maquinaria_id if registro.ID_Maquinaria is not None else None
                    causa = registro.Causa if registro.Causa is not None else ''
                    diagnostico = registro.Diagnostico if registro.Diagnostico is not None else ''
                    causaraiz = registro.CausaRaiz if registro.CausaRaiz is not None else ''

                    cursor.execute("SELECT COUNT(*) FROM ParosProduccion WHERE ID_Paro = ?", (registro.ID_Paro,))
                    existe = cursor.fetchone()[0] > 0

                    if existe:
                        # Actualizar el registro
                        cursor.execute("""UPDATE ParosProduccion 
                                          SET ID_Cliente = ?, OrdenFabricacionSAP = ?, ID_Producto = ?, 
                                              FechaParo = ?, HoraInicio = ?, HoraFin = ?, 
                                              TiempoMuerto = ?, PersonasAfectadas = ?, 
                                              MO = ?, ID_Proceso = ?, ID_Maquinaria = ?, 
                                              Causa = ?, Diagnostico = ?, CausaRaiz = ?, SYNC = ? 
                                          WHERE ID_Paro = ?""",
                                       (id_cliente, orden_fabricacion, id_producto, 
                                        fecha_paro, hora_inicio, 
                                        hora_fin, tiempo_muerto, 
                                        personas_afectadas, mo, 
                                        id_proceso, id_maquinaria, 
                                        causa, diagnostico, causaraiz, True, registro.ID_Paro))

                    else:
                        cursor.execute("SET IDENTITY_INSERT ParosProduccion ON")
                        cursor.execute("""INSERT INTO ParosProduccion (ID_Paro, ID_Cliente, OrdenFabricacionSAP, 
                                          ID_Producto, FechaParo, HoraInicio, HoraFin, 
                                          TiempoMuerto, PersonasAfectadas, MO, 
                                          ID_Proceso, ID_Maquinaria, Causa, Diagnostico, CausaRaiz, SYNC) 
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                       (registro.ID_Paro, 
                                        id_cliente, orden_fabricacion, 
                                        id_producto, fecha_paro, 
                                        hora_inicio, hora_fin, 
                                        tiempo_muerto, personas_afectadas, 
                                        mo, id_proceso, id_maquinaria, 
                                        causa, diagnostico, causaraiz, True))
                        cursor.execute("SET IDENTITY_INSERT ParosProduccion OFF")

                    # Marcar como sincronizado en la base de datos local
                    registro.SYNC = True
                    registro.save(using='spf_calidad')

            conn.commit()

    except Exception as e:
        messages.error(request, f'Error al sincronizar los datos: {str(e)}', extra_tags='sync')
        return redirect(reverse('production:production'))

    messages.success(request, 'Sincronización exitosa.', extra_tags='sync')
    return redirect(reverse('production:production'))


@login_required
def sync_procesos_view(request):
    registros_proc_no_sync = Procesos.objects.using('spf_info').filter(SYNC=False)

    server_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=QBSERVER\\SQLEXPRESS;"
        "Database=SPF_Info;"
        "UID=it;"
        "PWD=sqlSPF#2024;"
    )

    try:
        with pyodbc.connect(server_conn_str) as conn:
            cursor = conn.cursor()

            for registro_proc in registros_proc_no_sync:
                if getattr(registro_proc, 'DELETED', False):
                    cursor.execute("DELETE FROM Procesos WHERE ID_Proc = ?", (registro_proc.ID_Proc,))
                else:
                    cursor.execute("SELECT * FROM Procesos WHERE ID_Proc = ?", (registro_proc.ID_Proc,))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        # Actualizar el registro
                        cursor.execute(
                            """
                            UPDATE Procesos
                            SET 
                                Nombre_Proc = ?,
                                Estado = ?,
                                SYNC = 1
                            WHERE ID_Proc = ?
                            """,
                            (registro_proc.Nombre_Pro, registro_proc.Estado_Pro, registro_proc.ID_Pro)
                        )
                    else:
                        # Insertar un nuevo registro
                        cursor.execute(
                            """
                            INSERT INTO Procesos (ID_Proc, Nombre_Proc, Estado, SYNC)
                            VALUES (?, ?, ?, 1)
                            """,
                            (registro_proc.ID_Pro, registro_proc.Nombre_Pro, registro_proc.Estado_Pro)
                        )

                # Marcar como sincronizado en la base de datos local
                registro_proc.SYNC = True
                registro_proc.save(using='spf_info')

            conn.commit()

    except Exception as e:
        messages.error(request, f'Error al sincronizar procesos: {str(e)}')
        return redirect('production:registro')

    messages.success(request, 'Sincronización de procesos exitosa.')
    return redirect('production:registro')

@login_required
def sync_maquinaria_view(request):
    registros_maq_no_sync = Maquinaria.objects.using('spf_info').filter(SYNC=False)

    server_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=QBSERVER\\SQLEXPRESS;"
        "Database=SPF_Info;"
        "UID=it;"
        "PWD=sqlSPF#2024;"
    )

    try:
        with pyodbc.connect(server_conn_str) as conn:
            cursor = conn.cursor()

            for registro_maq in registros_maq_no_sync:
                if getattr(registro_maq, 'DELETED', False):
                    cursor.execute("DELETE FROM Maquinaria WHERE ID_Maquinaria = ?", (registro_maq.ID_Maquinaria,))
                else:
                    cursor.execute("SELECT * FROM Maquinaria WHERE ID_Maquinaria = ?", (registro_maq.ID_Maquinaria,))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        # Actualizar el registro
                        cursor.execute(
                            """
                            UPDATE Maquinaria
                            SET 
                                DescripcionMaq = ?,
                                AreaMaq = ?,
                                Estado = ?,
                                SYNC = 1
                            WHERE ID_Maquinaria = ?
                            """,
                            (registro_maq.DescripcionMaq, registro_maq.AreaMaq, registro_maq.Estado, registro_maq.ID_Maquinaria)
                        )
                    else:
                        # Insertar un nuevo registro
                        cursor.execute(
                            """
                            INSERT INTO Maquinaria (ID_Maquinaria, DescripcionMaq, AreaMaq, Estado, SYNC)
                            VALUES (?, ?, ?, ?, 1)
                            """,
                            (registro_maq.ID_Maquinaria, registro_maq.DescripcionMaq, registro_maq.AreaMaq, registro_maq.Estado)
                        )

                # Marcar como sincronizado en la base de datos local
                registro_maq.SYNC = True
                registro_maq.save(using='spf_info')

            conn.commit()

    except Exception as e:
        messages.error(request, f'Error al sincronizar maquinarias: {str(e)}')
        return redirect('production:registro')

    messages.success(request, 'Sincronización de maquinarias exitosa.')
    return redirect('production:registro')