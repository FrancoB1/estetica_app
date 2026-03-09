from django.contrib import admin
from datetime import date
from django.db.models import Q

from usuarios.models import Empleado
from .models import (
    Turno,
    ServicioPrestado,
    CajaDiaria,
    ReporteMensualEmpleado,
    Disponibilidad,
)


# ─────────────────────────────
# Helpers
# ─────────────────────────────

def es_admin(user):
    return user.is_authenticated and getattr(user, 'rol', None) == 'admin'


def caja_cerrada(fecha):
    return CajaDiaria.objects.filter(fecha=fecha, cerrada=True).exists()


# ─────────────────────────────
# Inline: Servicios prestados
# ─────────────────────────────

class ServicioPrestadoInline(admin.TabularInline):
    model = ServicioPrestado
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "empleado":

            object_id = request.resolver_match.kwargs.get('object_id')
            turno = None

            if object_id:
                try:
                    turno = Turno.objects.get(pk=object_id)
                except Turno.DoesNotExist:
                    turno = None

            if turno:

                empleados_validos = []

                for empleado in Empleado.objects.all():

                    # 1️⃣ Evitar solapamiento
                    conflictos = ServicioPrestado.objects.filter(
                        empleado=empleado,
                        turno__fecha=turno.fecha
                    ).filter(
                        Q(turno__hora_inicio__lt=turno.hora_fin) &
                        Q(turno__hora_fin__gt=turno.hora_inicio)
                    )

                    if conflictos.exists():
                        continue

                    # 2️⃣ MODELO B — Disponibilidad solo si existe
                    disponibilidades = Disponibilidad.objects.filter(
                        empleado=empleado,
                        fecha=turno.fecha
                    )

                    if disponibilidades.exists():
                        dentro_de_bloque = disponibilidades.filter(
                            hora_inicio__lte=turno.hora_inicio,
                            hora_fin__gte=turno.hora_fin
                        )

                        if not dentro_de_bloque.exists():
                            continue

                    empleados_validos.append(empleado.pk)

                kwargs["queryset"] = Empleado.objects.filter(pk__in=empleados_validos)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj=None):
        if obj and caja_cerrada(obj.fecha):
            return False
        return super().has_add_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and caja_cerrada(obj.fecha):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and caja_cerrada(obj.fecha):
            return False
        return super().has_delete_permission(request, obj)


# ─────────────────────────────
# Turnos
# ─────────────────────────────

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):

    inlines = [ServicioPrestadoInline]

    list_display = (
        'cliente_nombre',
        'cliente_apellido',
        'fecha',
        'hora_inicio',
        'hora_fin',
        'estado',
        'total_turno',
        'resumen_por_empleado',
    )

    readonly_fields = (
        'total_turno',
        'resumen_por_empleado',
    )

    def resumen_por_empleado(self, obj):
        totales = obj.total_por_empleado()
        if not totales:
            return "-"

        return ", ".join(
            f"{empleado}: ${monto}"
            for empleado, monto in totales.items()
        )

    resumen_por_empleado.short_description = "Pago por empleado"

    def has_change_permission(self, request, obj=None):
        if obj and caja_cerrada(obj.fecha):
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if caja_cerrada(date.today()):
            return False
        return super().has_add_permission(request)


# ─────────────────────────────
# Caja diaria
# ─────────────────────────────

@admin.register(CajaDiaria)
class CajaDiariaAdmin(admin.ModelAdmin):

    list_display = (
        'fecha',
        'total_servicios',
        'total_empleados',
        'ganancia',
        'cerrada',
    )

    list_filter = ('cerrada',)
    ordering = ('-fecha',)

    def has_module_permission(self, request):
        return es_admin(request.user)

    def has_view_permission(self, request, obj=None):
        return es_admin(request.user)

    def has_add_permission(self, request):
        return es_admin(request.user)

    def has_change_permission(self, request, obj=None):
        return es_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        return False


# ─────────────────────────────
# Reporte mensual por empleado
# ─────────────────────────────

@admin.register(ReporteMensualEmpleado)
class ReporteMensualEmpleadoAdmin(admin.ModelAdmin):

    change_list_template = "admin/reporte_mensual_empleado.html"

    def has_module_permission(self, request):
        return es_admin(request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        hoy = date.today()
        anio = int(request.GET.get('anio', hoy.year))
        mes = int(request.GET.get('mes', hoy.month))

        data = ServicioPrestado.objects.total_por_empleado_mes(anio, mes)

        context = {
            'data': data,
            'anio': anio,
            'mes': mes,
        }

        return super().changelist_view(request, extra_context=context)


admin.site.register(Disponibilidad)