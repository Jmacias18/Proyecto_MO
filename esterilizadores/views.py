# views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import TempEsterilizadores, Refrigerador
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
def registrotemp(request):
    if request.method == 'POST':
        form = TempEsterilizadoresForm(request.POST)
        if form.is_valid():
            temp_esterilizador = form.save(commit=False)
            temp_esterilizador.Fecha = form.cleaned_data['Fecha']
            temp_esterilizador.Hora = form.cleaned_data['Hora']
            temp_esterilizador.SYNC = False
            print(f"Datos a guardar: {temp_esterilizador.__dict__}")  # Agrega este print para ver los datos
            temp_esterilizador.save()  # Usar la base de datos por defecto
            messages.success(request, 'Registro guardado exitosamente.')
            return redirect('esterilizadores:tempester')  # Redirigir a una página de éxito
        else:
            messages.error(request, 'Error al guardar el registro. Por favor, verifica los datos ingresados.')
            print(f"Errores del formulario: {form.errors}")  # Agrega este print para ver los errores del formulario
    else:
        form = TempEsterilizadoresForm()

    # Recuperar todos los refrigeradores
    refrigeradores = Refrigerador.objects.all()

    # Pasar los refrigeradores y el formulario a la plantilla
    return render(request, 'esterilizadores/registrotemp.html', {'form': form, 'refrigeradores': refrigeradores})
@login_required
def sync_data_view(request):
    # Obtener registros no sincronizados de la base de datos local
    registros_no_sync = TempEsterilizadores.objects.using('default').filter(SYNC=False)

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
                    cursor.execute("DELETE FROM TemperaturaEsterilizadores WHERE ID_TempEsterilizadores = ?", (registro.ID_TempEsterilizador,))
                else:
                    fecha = registro.Fecha if registro.Fecha is not None else date.today()
                    hora = registro.Hora if registro.Hora is not None else '00:00:00'
                    id_refrigerador = registro.ID_Refrigerador_id if registro.ID_Refrigerador is not None else None
                    tempc = registro.TempC if registro.TempC is not None else 0
                    tempf = registro.TempF if registro.TempF is not None else 0
                    acorrectiva = registro.ACorrectiva if registro.ACorrectiva is not None else ''
                    apreventiva = registro.APreventiva if registro.APreventiva is not None else ''
                    observacion = registro.Observacion if registro.Observacion is not None else ''
                    inspecciono = registro.Inspecciono if registro.Inspecciono is not None else None
                    verifico = registro.Verifico if registro.Verifico is not None else None

                    cursor.execute("SELECT COUNT(*) FROM TemperaturaEsterilizadores WHERE ID_TempEsterilizadores = ?", (registro.ID_TempEsterilizadores,))
                    existe = cursor.fetchone()[0] > 0

                    if existe:
                        # Actualizar el registro
                        cursor.execute("""UPDATE TemperaturaEsterilizadores 
                                          SET Fecha = ?, Hora = ?, ID_Refrigerador = ?, 
                                              TempC = ?, TempF = ?, ACorrectiva = ?, 
                                              APreventiva = ?, Observacion = ?, 
                                              Inspecciono = ?, Verifico = ?,SYNC = ? 
                                          WHERE ID_TempEsterilizadores = ?""",
                                       (fecha, hora, id_refrigerador, 
                                        tempc, tempf, 
                                        acorrectiva, apreventiva, 
                                        observacion, inspecciono, 
                                        verifico, True, registro.ID_TempEsterilizadores))

                    else:
                        cursor.execute("SET IDENTITY_INSERT TemperaturaEsterilizadores ON")
                        cursor.execute("""INSERT INTO TemperaturaEsterilizadores (ID_TempEsterilizadores, Fecha, Hora, ID_Refrigerador, 
                                              TempC, TempF, ACorrectiva, 
                                              APreventiva, Observacion, 
                                              Inspecciono, Verifico, SYNC) 
                                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                       (registro.ID_TempEsterilizadores, 
                                        fecha, hora, id_refrigerador, 
                                        tempc, tempf, 
                                        acorrectiva, apreventiva, 
                                        observacion, inspecciono, 
                                        verifico, True))
                        cursor.execute("SET IDENTITY_INSERT TemperaturaEsterilizadores OFF")

                    # Marcar como sincronizado en la base de datos local
                    registro.SYNC = True
                    registro.save(using='default')

            conn.commit()

    except Exception as e:
        messages.error(request, f'Error al sincronizar los datos: {str(e)}')
        return redirect('esterilizadores:tempester')

    messages.success(request, 'Sincronización exitosa.')
    return redirect('esterilizadores:tempester')
