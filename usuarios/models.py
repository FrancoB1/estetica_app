from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ES_ADMIN = 'admin'
    ES_EMPLEADO = 'empleado'

    ROLES = [
        (ES_ADMIN, 'Administrador'),
        (ES_EMPLEADO, 'Empleado'),
    ]

    rol = models.CharField(
        max_length=10,
        choices=ROLES,
        default=ES_EMPLEADO
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class Empleado(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='empleado'
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username
