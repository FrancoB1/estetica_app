from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Empleado


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Rol y contacto', {
            'fields': ('rol', 'telefono'),
        }),
    )

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'rol',
        'is_staff',
        'is_active',
    )

    list_filter = ('rol', 'is_staff', 'is_active')

    search_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
    )


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'activo')
    list_filter = ('activo',)
    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
    )
