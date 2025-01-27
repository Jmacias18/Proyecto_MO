from django.contrib import admin, messages
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Create groups and assign permissions
        groups = ['Calidad', 'Producción', 'IT']
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                # Assign permissions to the group
                content_type = ContentType.objects.get_for_model(CustomUser)
                permissions = Permission.objects.filter(content_type=content_type)
                group.permissions.set(permissions)
                group.save()