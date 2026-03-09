from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crear usuario admin inicial"

    def handle(self, *args, **kwargs):

        if not Usuario.objects.filter(username="admin").exists():

            Usuario.objects.create_superuser(
                username="admin",
                email="admin@admin.com",
                password="admin123",
                rol="admin"
            )

            self.stdout.write(self.style.SUCCESS("Admin creado correctamente"))

        else:
            self.stdout.write("El admin ya existe")