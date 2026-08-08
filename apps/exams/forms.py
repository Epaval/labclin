from django import forms
from .models import Examen


class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = [
            "nombre_completo",
            "valores_ref",
            "perfil",
            "activo",
        ]
        widgets = {
            "nombre_completo": forms.TextInput(attrs={
                "placeholder": "Ej: Hematología completa",
            }),
            "valores_ref": forms.TextInput(attrs={
                "placeholder": "Valores de referencia...",
                
            }),
            "perfil": forms.TextInput(attrs={
                "placeholder": "Ej: Hematología",
            }),
        }
