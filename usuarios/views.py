from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Sum, F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import logout

from turnos.models import ServicioPrestado, Turno


# ─────────────────────────────
# LOGIN
# ─────────────────────────────

class LoginUsuarioView(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user

        if user.rol == 'admin':
            return reverse_lazy('panel_admin')
        else:
            return reverse_lazy('panel_empleado')


# ─────────────────────────────
# PANEL GENERAL (si lo usás)
# ─────────────────────────────

@login_required
def panel(request):
    return render(request, 'usuarios/panel.html')


# ─────────────────────────────
# PANEL ADMIN
# ─────────────────────────────

@login_required
def panel_admin(request):

    if request.user.rol != 'admin':
        return redirect('panel_empleado')

    hoy = date.today()

    turnos_hoy = (
        Turno.objects
        .filter(fecha=hoy)
        .order_by('hora_inicio')
        .prefetch_related(
            'servicios_prestados__empleado__usuario',
            'servicios_prestados__servicio'
        )
    )

    servicios_hoy = ServicioPrestado.objects.filter(
        turno__fecha=hoy,
        turno__estado='finalizado'
    )

    total_facturado = servicios_hoy.aggregate(
        total=Sum('servicio__precio')
    )['total'] or Decimal('0.00')

    total_comisiones = servicios_hoy.aggregate(
        total=Sum(
            F('servicio__precio') *
            F('servicio__porcentaje_empleado') / 100
        )
    )['total'] or Decimal('0.00')

    ganancia_local = total_facturado - total_comisiones

    # ─────────────────────────────
    # RESUMEN DEL DÍA POR EMPLEADO
    # ─────────────────────────────

    from usuarios.models import Empleado

    empleados = Empleado.objects.filter(activo=True)

    resumen_empleados = []

    for empleado in empleados:

        servicios = ServicioPrestado.objects.filter(
            empleado=empleado,
            turno__fecha=hoy,
            turno__estado='finalizado'
        )

        total_generado = servicios.aggregate(
            total=Sum('servicio__precio')
        )['total'] or Decimal('0.00')

        total_comision = servicios.aggregate(
            total=Sum(
                F('servicio__precio') *
                F('servicio__porcentaje_empleado') / 100
            )
        )['total'] or Decimal('0.00')

        resumen_empleados.append({
            "nombre": str(empleado),
            "servicios": servicios.count(),
            "total": total_generado,
            "comision": total_comision
        })

    resumen_empleados = sorted(
        resumen_empleados,
        key=lambda x: x["total"],
        reverse=True
    )

    context = {
        "hoy": hoy,
        "total_facturado": total_facturado,
        "total_comisiones": total_comisiones,
        "ganancia_local": ganancia_local,
        "total_servicios": servicios_hoy.count(),
        "turnos_hoy": turnos_hoy,
        "resumen_empleados": resumen_empleados,
    }

    return render(request, "usuarios/panel_admin.html", context)


# ─────────────────────────────
# PANEL EMPLEADO – DASHBOARD
# ─────────────────────────────

@login_required
def panel_empleado(request):

    if request.user.rol not in ['empleado', 'admin']:
        return redirect('home')

    empleado = None

    try:
        empleado = request.user.empleado
    except:
        pass

    hoy = date.today()

    servicios_hoy = ServicioPrestado.objects.filter(
        empleado=empleado,
        turno__fecha=hoy,
        turno__estado='finalizado'
    )

    total_generado_hoy = servicios_hoy.aggregate(
        total=Sum('servicio__precio')
    )['total'] or Decimal('0.00')

    total_comision_hoy = servicios_hoy.aggregate(
        total=Sum(
            F('servicio__precio') *
            F('servicio__porcentaje_empleado') / 100
        )
    )['total'] or Decimal('0.00')

    servicios_mes = ServicioPrestado.objects.filter(
        empleado=empleado,
        turno__fecha__year=hoy.year,
        turno__fecha__month=hoy.month,
        turno__estado='finalizado'
    )

    total_generado_mes = servicios_mes.aggregate(
        total=Sum('servicio__precio')
    )['total'] or Decimal('0.00')

    total_comision_mes = servicios_mes.aggregate(
        total=Sum(
            F('servicio__precio') *
            F('servicio__porcentaje_empleado') / 100
        )
    )['total'] or Decimal('0.00')

    context = {
        "hoy": hoy,
        "total_generado_hoy": total_generado_hoy,
        "total_comision_hoy": total_comision_hoy,
        "total_generado_mes": total_generado_mes,
        "total_comision_mes": total_comision_mes,
    }

    return render(request, "usuarios/panel_empleado.html", context)


# ─────────────────────────────
# HOME REDIRECT
# ─────────────────────────────

def home(request):

    if request.user.is_authenticated:

        if request.user.rol == 'admin':
            return redirect('panel_admin')

        return redirect('panel_empleado')

    return redirect('login')
@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect("login")