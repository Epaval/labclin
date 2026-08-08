from django import forms

from apps.doctors.models import Medico
from apps.exams.models import Examen

from .models import Expediente, Paciente


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            "nombres", "apellidos", "ci", "direccion",
            "telefono", "email", "sexo", "fecha_nac",
        ]
        widgets = {
            "nombres": forms.TextInput(attrs={"placeholder": "Ej: María"}),
            "apellidos": forms.TextInput(attrs={"placeholder": "Ej: González"}),
            "ci": forms.TextInput(attrs={"placeholder": "Ej: V12345678"}),
            "direccion": forms.Textarea(attrs={"rows": 2, "placeholder": "Dirección completa"}),
            "telefono": forms.TextInput(attrs={"placeholder": "+584141234567"}),
            "email": forms.EmailInput(attrs={"placeholder": "email@ejemplo.com"}),
            "fecha_nac": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_fecha_nac(self):
        from django.utils import timezone

        fecha = self.cleaned_data.get("fecha_nac")
        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura")
        return fecha


class ExpedienteForm(forms.ModelForm):
    examenes = forms.ModelMultipleChoiceField(
        queryset=Examen.objects.filter(activo=True),
        required=True,
        label="Exámenes a realizar",
    )
    medicos = forms.ModelMultipleChoiceField(
        queryset=Medico.objects.filter(activo=True),
        required=False,
        label="Médicos solicitantes (opcional)",
        widget=forms.SelectMultiple(attrs={"size": 4}),
    )

    class Meta:
        model = Expediente
        fields = ["paciente", "bioanalista", "observaciones"]
        widgets = {
            "observaciones": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Indicaciones o notas de la orden...",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["paciente"].queryset = (
            Paciente.objects.filter(activo=True).order_by("apellidos", "nombres")
        )
