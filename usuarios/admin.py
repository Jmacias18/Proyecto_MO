# usuarios/admin.py
from django.contrib import admin, messages
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def delete_model(self, request, obj):
        if obj == request.user:
            self.message_user(request, "No puedes eliminar tu propio usuario.", level=messages.ERROR)
        else:
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if request.user in queryset:
            self.message_user(request, "No puedes eliminar tu propio usuario.", level=messages.ERROR)
            queryset = queryset.exclude(pk=request.user.pk)
        super().delete_queryset(request, queryset)