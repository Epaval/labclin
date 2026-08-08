from django.contrib import admin

from .models import CostoExamen, Examen


@admin.register(Examen)
class ExamenAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "perfil", "activo", "costo_actual")
    search_fields = ("nombre_completo", "perfil")
    list_filter = ("activo", "perfil")


@admin.register(CostoExamen)
class CostoExamenAdmin(admin.ModelAdmin):
    list_display = ("examen", "precio", "activo", "ultima_fecha_act")
    list_filter = ("activo",)
