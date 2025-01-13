import pyodbc
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from .models import Refrigeradores
from django.db import connection
from django.utils.translation import gettext_lazy as _

@admin.register(Refrigeradores)
class RefrigeradoresAdmin(admin.ModelAdmin):
    list_display = ('ID_Refrigerador', 'DescripcionRef', 'Min', 'Max', 'TipoRefrigerador', 'SYNC', 'estado_display', 'edit_link')
    search_fields = ('DescripcionRef',)
    list_filter = ('TipoRefrigerador', 'estado', 'SYNC')

    def estado_display(self, obj):
        return "Activo" if obj.estado else "Inactivo"
    estado_display.short_description = 'Estado'

    def edit_link(self, obj):
        url = f'/admin/temperature/refrigeradores/{obj.ID_Refrigerador}/change/'
        return format_html('<a href="{}">Editar</a>', url)

    edit_link.short_description = 'Acciones'

    def sync_all_refrigeradores(self, request, queryset):
        # Realizamos la sincronización y revisamos el resultado
        success = self.perform_sync(queryset)
        
        # Enviamos el mensaje adecuado según el resultado de la sincronización
        if success:
            self.message_user(request, 'Sincronización completa de refrigeradores seleccionados.', level='success')
        else:
            self.message_user(request, 'Error al sincronizar los refrigeradores. Verifique la conexión a internet.', level='error')

    sync_all_refrigeradores.short_description = "Sincronizar refrigeradores seleccionados"

    def perform_sync(self, queryset):
        """Realiza la sincronización de los refrigeradores seleccionados, sin enviar mensajes"""
        server_conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=QBSERVER\\SQLEXPRESS;"
            "Database=SPF_Info;"
            "UID=it;"
            "PWD=sqlSPF#2024;"
        )

        try:
            # Intentar conectarse al servidor SQL con un timeout de 5 segundos
            with pyodbc.connect(server_conn_str, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("SET IDENTITY_INSERT Refrigeradores ON")

                for refrigerador in queryset:
                    cursor.execute(""" 
                        IF EXISTS (SELECT 1 FROM Refrigeradores WHERE ID_Refrigerador = ?)
                        BEGIN
                            UPDATE Refrigeradores
                            SET 
                                DescripcionRef = ?, 
                                Min = ?, 
                                Max = ?, 
                                TipoRefrigerador = ?, 
                                SYNC = 1, 
                                estado = ?
                            WHERE ID_Refrigerador = ?
                        END
                        ELSE
                        BEGIN
                            INSERT INTO Refrigeradores (ID_Refrigerador, DescripcionRef, Min, Max, TipoRefrigerador, SYNC, estado)
                            VALUES (?, ?, ?, ?, ?, 1, ?)
                        END
                    """, (
                        refrigerador.ID_Refrigerador,
                        refrigerador.DescripcionRef,
                        refrigerador.Min,
                        refrigerador.Max,
                        refrigerador.TipoRefrigerador,
                        refrigerador.estado,
                        refrigerador.ID_Refrigerador,
                        refrigerador.ID_Refrigerador,
                        refrigerador.DescripcionRef,
                        refrigerador.Min,
                        refrigerador.Max,
                        refrigerador.TipoRefrigerador,
                        refrigerador.estado
                    ))

                    refrigerador.SYNC = True  # Marca como sincronizado en local
                    refrigerador.save(using='spf_info')

                cursor.execute("SET IDENTITY_INSERT Refrigeradores OFF")
                conn.commit()

            return True  # Indica que la sincronización fue exitosa

        except pyodbc.OperationalError as e:
            # Error de conexión (no se pudo conectar al servidor)
            print(f"Error de conexión: {str(e)}")  # También puedes imprimir el error en el log para depuración
            return False  # Indica que hubo un error, no se completó la sincronización

        except pyodbc.InterfaceError as e:
            # Error de interfaz (por ejemplo, sin conexión a la base de datos)
            print(f"Error de interfaz de base de datos: {str(e)}")
            return False  # Indica que hubo un error, no se completó la sincronización

        except Exception as e:
            # Cualquier otro error
            print(f'Error general: {str(e)}')
            return False  # Indica que hubo un error, no se completó la sincronización

    def change_view(self, request, object_id, form_url='', extra_context=None):
        response = super().change_view(request, object_id, form_url, extra_context)
        return response

    def changelist_view(self, request, extra_context=None):
            """Agrega el botón para ir a la vista 'temperature'"""
            # Añadimos el botón para redirigir a la vista de control de temperatura
            if request.method == "POST" and "sync_all" in request.POST:
                success = self.perform_sync(Refrigeradores.objects.all())
                if success:
                    self.message_user(request, 'Sincronización completa de todos los refrigeradores.', level='success')
                else:
                    self.message_user(request, 'Error al sincronizar todos los refrigeradores. Verifique la conexión a internet.', level='error')
                return redirect(request.path)

            # Redirigir a la vista del control de temperatura cuando se presiona el botón
            extra_context = extra_context or {}
            extra_context['temperature_url'] = reverse('temperature:temperature')

            return super().changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        if change:
            obj.SYNC = False  # Marca como no sincronizado al editar
        obj.save(using='spf_info')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'SYNC' in form.base_fields:
            form.base_fields['SYNC'].disabled = True
        return form
