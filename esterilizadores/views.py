# views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import TempEsterilizadores, Maquinaria
from .forms import TempEsterilizadoresForm
from usuarios.models import CustomUser
from django.contrib.auth.decorators import login_required
import pyodbc
from datetime import date

@login_required
def mostrar_datos(request):
    # Recupera todos los registros de TempEsterilizadores
    registros = TempEsterilizadores.objects.all()

    return render(request, 'esterilizadores/tempester.html', {'registros': registros})

@login_required
def borrar_temp(request, id):
    registro = get_object_or_404(TempEsterilizadores, ID_TempEsterilizador=id)
    if request.method == 'POST':
        registro.delete()
        messages.success(request, 'Registro eliminado exitosamente.')
        return redirect('esterilizadores:tempester')
    return render(request, 'esterilizadores/confirmar_borrar.html', {'registro': registro})

@login_required
def modificar_temp(request, id):
    registro = get_object_or_404(TempEsterilizadores, ID_TempEsterilizador=id)
    if request.method == 'POST':
        form = TempEsterilizadoresForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro modificado exitosamente.')
            return redirect('esterilizadores:tempester')
    else:
        form = TempEsterilizadoresForm(instance=registro)

    # Filtrar las maquinarias que contienen "Esterilizador #"
    maquinarias = Maquinaria.objects.using('spf_info').filter(DescripcionMaq__startswith='Esterilizador #')

    return render(request, 'esterilizadores/modificartemp.html', {'form': form, 'registro': registro, 'maquinarias': maquinarias})
@login_required
def registrotemp(request):
    if request.method == 'POST':
        form = TempEsterilizadoresForm(request.POST)
        if form.is_valid():
            temp_esterilizador = form.save(commit=False)
            temp_esterilizador.Fecha = form.cleaned_data['Fecha']
            temp_esterilizador.Hora = form.cleaned_data['Hora']
            temp_esterilizador.SYNC = False
            temp_esterilizador.Inspecciono = 0  # Establecer Inspecciono en 0
            temp_esterilizador.Verifico = 0  # Establecer Verifico en 0
            temp_esterilizador.save(using='spf_calidad')  # Usar la base de datos 'spf_calidad'
            messages.success(request, 'Registro guardado exitosamente.')
            return redirect('esterilizadores:tempester')  # Redirigir a una página de éxito
        else:
            messages.error(request, 'Error al guardar el registro. Por favor, verifica los datos ingresados.')
    else:
        form = TempEsterilizadoresForm()

    # Filtrar las maquinarias que contienen "Esterilizador #"
    maquinarias = Maquinaria.objects.using('spf_info').filter(DescripcionMaq__startswith='Esterilizador #')

    # Pasar las maquinarias y el formulario a la plantilla
    return render(request, 'esterilizadores/registrotemp.html', {'form': form, 'maquinarias': maquinarias})

@login_required
def sync_data_view(request):
    # Obtener registros no sincronizados de la base de datos local
    registros_no_sync = TempEsterilizadores.objects.using('spf_calidad').filter(SYNC=False)

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
                    cursor.execute("DELETE FROM TemperaturaEsterilizadores WHERE ID_TempEsterilizador = ?", (registro.ID_TempEsterilizador,))
                else:
                    fecha = registro.Fecha if registro.Fecha is not None else date.today()
                    hora = registro.Hora if registro.Hora is not None else '00:00:00'
                    id_maquinaria = registro.ID_Maquinaria_id if registro.ID_Maquinaria is not None else None
                    tempc = registro.TempC if registro.TempC is not None else 0
                    tempf = registro.TempF if registro.TempF is not None else 0
                    acorrectiva = registro.ACorrectiva if registro.ACorrectiva is not None else ''
                    apreventiva = registro.APreventiva if registro.APreventiva is not None else ''
                    observacion = registro.Observaciones if registro.Observaciones is not None else ''
                    inspecciono = registro.Inspecciono if registro.Inspecciono is not None else None
                    verifico = registro.Verifico if registro.Verifico is not None else None

                    cursor.execute("SELECT COUNT(*) FROM TemperaturaEsterilizadores WHERE ID_TempEsterilizador = ?", (registro.ID_TempEsterilizador,))
                    existe = cursor.fetchone()[0] > 0

                    if existe:
                        # Actualizar el registro
                        cursor.execute("""UPDATE TemperaturaEsterilizadores 
                                          SET Fecha = ?, Hora = ?, ID_Maquinaria = ?, 
                                              TempC = ?, TempF = ?, ACorrectiva = ?, 
                                              APreventiva = ?, Observaciones = ?, 
                                              Inspecciono = ?, Verifico = ?,SYNC = ? 
                                          WHERE ID_TempEsterilizador = ?""",
                                       (fecha, hora, id_maquinaria, 
                                        tempc, tempf, 
                                        acorrectiva, apreventiva, 
                                        observacion, inspecciono, 
                                        verifico, True, registro.ID_TempEsterilizador))

                    else:
                        cursor.execute("SET IDENTITY_INSERT TemperaturaEsterilizadores ON")
                        cursor.execute("""INSERT INTO TemperaturaEsterilizadores (ID_TempEsterilizador, Fecha, Hora, ID_Maquinaria, 
                                              TempC, TempF, ACorrectiva, 
                                              APreventiva, Observaciones, 
                                              Inspecciono, Verifico, SYNC) 
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                       (registro.ID_TempEsterilizador, 
                                        fecha, hora, id_maquinaria, 
                                        tempc, tempf, 
                                        acorrectiva, apreventiva, 
                                        observacion, inspecciono, 
                                        verifico, True))
                        cursor.execute("SET IDENTITY_INSERT TemperaturaEsterilizadores OFF")

                    # Marcar como sincronizado en la base de datos local
                    registro.SYNC = True
                    registro.save(using='spf_calidad')

            conn.commit()

    except Exception as e:
        messages.error(request, f'Error al sincronizar los datos: {str(e)}')
        return redirect('esterilizadores:tempester')

    messages.success(request, 'Sincronización exitosa.')
    return redirect('esterilizadores:tempester')


