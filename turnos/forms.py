from django import forms
from .models import Turno


class TurnoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = [
            'fecha',
            'hora_inicio',
            'hora_fin',
            'cliente_nombre',
            'cliente_apellido',
        ]
        widgets = {
            'fecha': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'hora_inicio': forms.TimeInput(
                attrs={'type': 'time'}
            ),
            'hora_fin': forms.TimeInput(
                attrs={'type': 'time'}
            ),
        }

    def save(self, commit=True):
        turno = super().save(commit=False)
        turno.estado = 'confirmado'
        if commit:
            turno.save()
        return turno
from .models import ServicioPrestado


class ServicioPrestadoForm(forms.ModelForm):
    class Meta:
        model = ServicioPrestado
        fields = ['servicio', ]


from django import forms
from .models import Disponibilidad


class DisponibilidadEmpleadoForm(forms.ModelForm):

    class Meta:
        model = Disponibilidad
        fields = ['fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }
