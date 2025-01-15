from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Procesos, Maquinaria, TipoProducto, Productos, ParosProduccion

# Personalización para el modelo Procesos
@admin.register(Procesos)
class ProcesosAdmin(admin.ModelAdmin):
    list_display = ('ID_Pro', 'Nombre_Pro', 'Estado_Pro', 'SYNC', 'action_links')
    actions = None  # Desactiva todas las acciones (como eliminar)
    
    # Establecer el campo 'SYNC' como solo lectura
    readonly_fields = ('SYNC',)

    def action_links(self, obj):
        edit_url = reverse('admin:production_procesos_change', args=[obj.ID_Pro])
        return format_html(
            '<a href="{}">Editar</a>', 
            edit_url
        )
    action_links.short_description = 'Acciones'

    # Desactivar la opción de eliminar
    def has_delete_permission(self, request, obj=None):
        return False


# Personalización para el modelo Maquinaria
@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ('ID_Maquinaria', 'DescripcionMaq', 'AreaMaq', 'Estado', 'SYNC', 'action_links')
    actions = None  # Desactiva todas las acciones (como eliminar)
    
    # Establecer el campo 'SYNC' como solo lectura
    readonly_fields = ('SYNC',)

    def action_links(self, obj):
        edit_url = reverse('admin:production_maquinaria_change', args=[obj.ID_Maquinaria])
        return format_html(
            '<a href="{}">Editar</a>', 
            edit_url
        )
    action_links.short_description = 'Acciones'

    # Desactivar la opción de eliminar
    def has_delete_permission(self, request, obj=None):
        return False

