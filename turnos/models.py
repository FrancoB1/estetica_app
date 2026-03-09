from collections import defaultdict
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, Q
from django.utils import timezone

from servicios.models import Servicio
from usuarios.models import Empleado


# ─────────────────────────────────────────────
# TURNO
# ─────────────────────────────────────────────
class Turno(models.Model):

    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    )

    cliente_nombre = models.CharField(max_length=100)
    cliente_apellido = models.CharField(max_length=100)
    cliente_telefono = models.CharField(max_length=20, blank=True)

    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )

    sena = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    creado = models.DateTimeField(auto_now_add=True)

    def total_turno(self):
        return sum(
            (sp.servicio.precio for sp in self.servicios_prestados.all()),
            Decimal('0.00')
        )

    def total_por_empleado(self):
        totales = defaultdict(Decimal)

        for sp in self.servicios_prestados.all():
            monto = (
                sp.servicio.precio *
                (Decimal(sp.servicio.porcentaje_empleado) / Decimal('100'))
            )
            totales[sp.empleado] += monto

        return dict(totales)

    def resumen_por_empleado(self):
        totales = self.total_por_empleado()

        if not totales:
            return "-"

        return ", ".join(
            f"{empleado}: ${monto:.2f}"
            for empleado, monto in totales.items()
        )

    def clean(self):

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                "La hora de inicio debe ser menor que la hora de fin."
            )

    def __str__(self):
        return f"{self.cliente_nombre} {self.cliente_apellido} - {self.fecha}"


# ─────────────────────────────────────────────
# SERVICIO PRESTADO
# ─────────────────────────────────────────────
class ServicioPrestadoQuerySet(models.QuerySet):

    def total_por_empleado_dia(self, fecha):
        return (
            self.filter(turno__fecha=fecha, turno__estado='finalizado')
            .values('empleado__usuario__username')
            .annotate(
                total=Sum(
                    F('servicio__precio') *
                    F('servicio__porcentaje_empleado') /
                    Decimal('100')
                )
            )
        )

    def total_por_empleado_mes(self, anio, mes):
        return (
            self.filter(
                turno__fecha__year=anio,
                turno__fecha__month=mes,
                turno__estado='finalizado'
            )
            .values('empleado__usuario__username')
            .annotate(
                total=Sum(
                    F('servicio__precio') *
                    F('servicio__porcentaje_empleado') /
                    Decimal('100')
                )
            )
        )


class ServicioPrestado(models.Model):

    turno = models.ForeignKey(
        Turno,
        on_delete=models.CASCADE,
        related_name='servicios_prestados'
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT
    )

    objects = ServicioPrestadoQuerySet.as_manager()

    def clean(self):

        if not self.turno_id or not self.empleado_id:
            return

        conflictos = ServicioPrestado.objects.filter(
            empleado=self.empleado,
            turno__fecha=self.turno.fecha,
        ).exclude(
            pk=self.pk
        ).exclude(
            turno=self.turno
        ).filter(
            Q(turno__hora_inicio__lt=self.turno.hora_fin) &
            Q(turno__hora_fin__gt=self.turno.hora_inicio)
        )

        if conflictos.exists():
            raise ValidationError(
                f"{self.empleado} ya tiene un turno en ese horario."
            )

        # MODELO B – disponibilidad solo si existe
        disponibilidades = Disponibilidad.objects.filter(
            empleado=self.empleado,
            fecha=self.turno.fecha
        )

        if disponibilidades.exists():

            disponibilidad_valida = disponibilidades.filter(
                hora_inicio__lte=self.turno.hora_inicio,
                hora_fin__gte=self.turno.hora_fin
            )

            if not disponibilidad_valida.exists():
                raise ValidationError(
                    f"{self.empleado} no tiene disponibilidad en ese horario."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.servicio} - {self.empleado}"


# ─────────────────────────────────────────────
# CAJA DIARIA
# ─────────────────────────────────────────────
class CajaDiaria(models.Model):

    fecha = models.DateField(unique=True)

    total_servicios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_empleados = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ganancia = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    cerrada = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)

    def calcular(self):
        servicios = ServicioPrestado.objects.filter(
            turno__fecha=self.fecha,
            turno__estado='finalizado'
        )

        total_servicios = servicios.aggregate(
            total=Sum('servicio__precio')
        )['total'] or Decimal('0.00')

        total_empleados = servicios.aggregate(
            total=Sum(
                F('servicio__precio') *
                F('servicio__porcentaje_empleado') /
                Decimal('100')
            )
        )['total'] or Decimal('0.00')

        self.total_servicios = total_servicios
        self.total_empleados = total_empleados
        self.ganancia = total_servicios - total_empleados

    def save(self, *args, **kwargs):
        if not self.cerrada:
            self.calcular()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Caja {self.fecha} - {'Cerrada' if self.cerrada else 'Abierta'}"


class ReporteMensualEmpleado(ServicioPrestado):
    class Meta:
        proxy = True
        verbose_name = "Reporte mensual por empleado"
        verbose_name_plural = "Reporte mensual por empleado"


# ─────────────────────────────────────────────
# DISPONIBILIDAD
# ─────────────────────────────────────────────
class Disponibilidad(models.Model):

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='disponibilidades'
    )

    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "hora_inicio"]

    def clean(self):

        # 🔹 Si aún no tiene empleado asignado, no validar
        if not self.empleado_id:
            return

        if self.fecha < timezone.localdate():
            raise ValidationError(
                "No se puede cargar disponibilidad en fechas pasadas."
            )

        if self.hora_inicio >= self.hora_fin:
            raise ValidationError(
                "La hora de inicio debe ser menor que la hora de fin."
            )

        conflicto = Disponibilidad.objects.filter(
            empleado_id=self.empleado_id,
            fecha=self.fecha
        ).filter(
            Q(hora_inicio__lt=self.hora_fin) &
            Q(hora_fin__gt=self.hora_inicio)
        )

        if self.pk:
            conflicto = conflicto.exclude(pk=self.pk)

        if conflicto.exists():
            raise ValidationError(
                "Este bloque se superpone con otra disponibilidad existente."
            )

    def save(self, *args, **kwargs):

        if self.pk:
            turnos_en_rango = ServicioPrestado.objects.filter(
                empleado=self.empleado,
                turno__fecha=self.fecha,
                turno__hora_inicio__lt=self.hora_fin,
                turno__hora_fin__gt=self.hora_inicio
            )

            if turnos_en_rango.exists():
                raise ValidationError(
                    "No se puede modificar esta disponibilidad porque tiene turnos dentro."
                )

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):

        turnos_en_rango = ServicioPrestado.objects.filter(
            empleado=self.empleado,
            turno__fecha=self.fecha,
            turno__hora_inicio__lt=self.hora_fin,
            turno__hora_fin__gt=self.hora_inicio
        )

        if turnos_en_rango.exists():
            raise ValidationError(
                "No se puede eliminar esta disponibilidad porque tiene turnos dentro."
            )

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado} - {self.fecha} ({self.hora_inicio}-{self.hora_fin})"