from django.urls import path
from .views import (
    agenda_dia,
    agenda_semana,
    agenda_empleado_hoy,
    resumen_empleado_hoy,
    resumen_empleado_mes,
    crear_turno_empleado,
    agregar_servicio_turno,
    disponibilidad_empleado,
    crear_disponibilidad_empleado,
    editar_disponibilidad_empleado,
    eliminar_disponibilidad_empleado,
)
from django.urls import path
from .views import (
    agenda_dia,
    agenda_semana,
    agenda_empleado_hoy,

    crear_turno_empleado,
    agregar_servicio_turno,

    disponibilidad_empleado,
    crear_disponibilidad_empleado,
    editar_disponibilidad_empleado,
    eliminar_disponibilidad_empleado,

    resumen_empleado_hoy,
    resumen_empleado_mes,
)

urlpatterns = [

    # --------------------------------------------------
    # AGENDA
    # --------------------------------------------------
    path('agenda/', agenda_dia, name='agenda_dia'),
    path('agenda/semana/', agenda_semana, name='agenda_semana'),
    path('agenda/empleado/', agenda_empleado_hoy, name='agenda_empleado'),

    # --------------------------------------------------
    # TURNOS
    # --------------------------------------------------
    path('nuevo/', crear_turno_empleado, name='turno_nuevo'),

    path(
        'turno/<int:turno_id>/agregar-servicio/',
        agregar_servicio_turno,
        name='agregar_servicio_turno'
    ),
path("mover-turno/", views.mover_turno, name="mover_turno"),

    # --------------------------------------------------
    # DISPONIBILIDAD
    # --------------------------------------------------
    path('disponibilidad/', disponibilidad_empleado, name='disponibilidad_empleado'),
    path('disponibilidad/nueva/', crear_disponibilidad_empleado, name='crear_disponibilidad_empleado'),
    path('disponibilidad/<int:pk>/editar/', editar_disponibilidad_empleado, name='editar_disponibilidad_empleado'),
    path('disponibilidad/<int:pk>/eliminar/', eliminar_disponibilidad_empleado, name='eliminar_disponibilidad_empleado'),

    # --------------------------------------------------
    # REPORTES EMPLEADO
    # --------------------------------------------------
    path('resumen/empleado/', resumen_empleado_hoy, name='resumen_empleado_hoy'),
    path('resumen/empleado/mes/', resumen_empleado_mes, name='resumen_empleado_mes'),

]