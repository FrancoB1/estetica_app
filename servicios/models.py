from django.db import models


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    duracion_minutos = models.PositiveIntegerField(
        help_text="Duración estimada del servicio en minutos"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio base del servicio"
    )
    activo = models.BooleanField(default=True)

    porcentaje_empleado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Porcentaje que recibe el empleado por este servicio"
    )


    def __str__(self):
        return f"{self.nombre} ({self.duracion_minutos} min)"
