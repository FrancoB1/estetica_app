from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        from usuarios.models import Usuario

        if not Usuario.objects.filter(username="admin").exists():
            Usuario.objects.create_superuser(
                username="admin",
                email="admin@admin.com",
                password="admin123",
                rol="admin"
            )