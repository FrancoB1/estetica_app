from datetime import date, timedelta, datetime
from collections import defaultdict
from decimal import Decimal

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.views.decorators.cache import never_cache

from .models import Turno, ServicioPrestado, Disponibilidad
from .forms import (
    TurnoEmpleadoForm,
    ServicioPrestadoForm,
    DisponibilidadEmpleadoForm
)


# ==========================================================
# AGENDA GENERAL
# ==========================================================

def agenda_dia(request):

    fecha_str = request.GET.get("fecha")

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            fecha = date.today()
    else:
        fecha = date.today()

    turnos = (
        Turno.objects
        .filter(fecha=fecha)
        .order_by("hora_inicio")
    )

    horas = [f"{h:02d}:00" for h in range(8, 21)]

    return render(request, "turnos/agenda_dia.html", {
        "fecha": fecha,
        "turnos": turnos,
        "horas": horas,
    })


def agenda_semana(request):

    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    turnos = (
        Turno.objects
        .filter(fecha__range=[inicio_semana, fin_semana])
        .order_by("fecha", "hora_inicio")
    )

    turnos_por_dia = defaultdict(list)

    for turno in turnos:
        turnos_por_dia[turno.fecha].append(turno)

    return render(request, "turnos/agenda_semana.html", {
        "inicio_semana": inicio_semana,
        "fin_semana": fin_semana,
        "turnos_por_dia": dict(turnos_por_dia),
    })


# ==========================================================
# AGENDA EMPLEADO
# ==========================================================

@login_required
def agenda_empleado_hoy(request):

    hoy = date.today()
    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    turnos = (
        Turno.objects
        .filter(
            fecha=hoy,
            servicios_prestados__empleado=empleado
        )
        .distinct()
        .order_by("hora_inicio")
    )

    return render(request, "turnos/agenda_empleado.html", {
        "fecha": hoy,
        "turnos": turnos,
    })


# ==========================================================
# RESUMEN EMPLEADO
# ==========================================================

@login_required
def resumen_empleado_hoy(request):

    hoy = date.today()
    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    servicios = (
        ServicioPrestado.objects
        .filter(
            turno__fecha=hoy,
            turno__estado="finalizado",
            empleado=empleado
        )
        .annotate(
            monto=F("servicio__precio") *
                  F("servicio__porcentaje_empleado") / Decimal("100")
        )
    )

    total = servicios.aggregate(total=Sum("monto"))["total"] or Decimal("0.00")

    return render(request, "turnos/resumen_empleado.html", {
        "fecha": hoy,
        "servicios": servicios,
        "total": total,
    })


@login_required
def resumen_empleado_mes(request):

    hoy = date.today()
    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    servicios = (
        ServicioPrestado.objects
        .filter(
            turno__fecha__year=hoy.year,
            turno__fecha__month=hoy.month,
            turno__estado="finalizado",
            empleado=empleado
        )
        .annotate(
            monto=F("servicio__precio") *
                  F("servicio__porcentaje_empleado") / Decimal("100")
        )
    )

    total = servicios.aggregate(total=Sum("monto"))["total"] or Decimal("0.00")

    return render(request, "turnos/resumen_empleado_mes.html", {
        "mes": hoy.strftime("%B %Y"),
        "servicios": servicios,
        "total": total,
    })


# ==========================================================
# TURNOS EMPLEADO
# ==========================================================

@login_required
@never_cache
def crear_turno_empleado(request):

    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    if request.method == "POST":

        turno_form = TurnoEmpleadoForm(request.POST)
        servicio_form = ServicioPrestadoForm(request.POST)

        if turno_form.is_valid() and servicio_form.is_valid():

            turno = turno_form.save()

            servicio_prestado = servicio_form.save(commit=False)
            servicio_prestado.turno = turno
            servicio_prestado.empleado = empleado
            servicio_prestado.save()

            return redirect("agenda_dia")

    else:

        turno_form = TurnoEmpleadoForm()
        servicio_form = ServicioPrestadoForm()

    return render(request, "turnos/turno_nuevo.html", {
        "turno_form": turno_form,
        "servicio_form": servicio_form,
    })


@login_required
@never_cache
def agregar_servicio_turno(request, turno_id):

    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    turno = get_object_or_404(Turno, id=turno_id)

    if request.method == "POST":

        form = ServicioPrestadoForm(request.POST)

        if form.is_valid():

            servicio_prestado = form.save(commit=False)
            servicio_prestado.turno = turno
            servicio_prestado.empleado = empleado
            servicio_prestado.save()

            return redirect("agenda_dia")

    else:
        form = ServicioPrestadoForm()

    return render(request, "turnos/agregar_servicio.html", {
        "turno": turno,
        "form": form
    })


# ==========================================================
# DISPONIBILIDAD EMPLEADO
# ==========================================================

@login_required
def disponibilidad_empleado(request):

    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    hoy = timezone.localdate()

    disponibilidades = (
        Disponibilidad.objects
        .filter(
            empleado=empleado,
            fecha__gte=hoy
        )
        .order_by("fecha", "hora_inicio")
    )

    return render(request, "turnos/disponibilidad_empleado.html", {
        "disponibilidades": disponibilidades,
        "hoy": hoy,
    })


@login_required
@never_cache
def crear_disponibilidad_empleado(request):

    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    if request.method == "POST":

        form = DisponibilidadEmpleadoForm(request.POST)

        if form.is_valid():

            disponibilidad = form.save(commit=False)
            disponibilidad.empleado = empleado
            disponibilidad.full_clean()
            disponibilidad.save()

            return redirect("disponibilidad_empleado")

    else:
        form = DisponibilidadEmpleadoForm()

    return render(request, "turnos/disponibilidad_form.html", {
        "form": form
    })


@login_required
@never_cache
def editar_disponibilidad_empleado(request, pk):

    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    disponibilidad = get_object_or_404(
        Disponibilidad,
        pk=pk,
        empleado=empleado
    )

    if request.method == "POST":

        form = DisponibilidadEmpleadoForm(
            request.POST,
            instance=disponibilidad
        )

        if form.is_valid():

            disponibilidad = form.save(commit=False)
            disponibilidad.empleado = empleado
            disponibilidad.full_clean()
            disponibilidad.save()

            return redirect("disponibilidad_empleado")

    else:
        form = DisponibilidadEmpleadoForm(instance=disponibilidad)

    return render(request, "turnos/disponibilidad_form.html", {
        "form": form
    })


@login_required
@never_cache
def eliminar_disponibilidad_empleado(request, pk):

    empleado = getattr(request.user, "empleado", None)

    if not empleado:
        return redirect("panel_empleado")

    disponibilidad = get_object_or_404(
        Disponibilidad,
        pk=pk,
        empleado=empleado
    )

    if request.method == "POST":
        disponibilidad.delete()
        return redirect("disponibilidad_empleado")

    return render(request, "turnos/disponibilidad_confirmar_eliminar.html", {
        "disponibilidad": disponibilidad
    })