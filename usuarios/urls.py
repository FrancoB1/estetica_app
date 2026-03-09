from django.urls import path
from .views import (
    LoginUsuarioView,
    panel_admin,
    panel_empleado,
    home,
    cerrar_sesion,
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginUsuarioView.as_view(), name='login'),

    path('panel/admin/', panel_admin, name='panel_admin'),
    path('panel/empleado/', panel_empleado, name='panel_empleado'),

    path('logout/', cerrar_sesion, name='logout'),
]