from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from django.conf import settings

from .licencias import (
    clave_valida,
    dias_restantes,
    estado_licencia,
    guardar_licencia,
    huella_maquina,
    tipo_licencia_actual,
)


class ActivacionView(View):
    def get(self, request):
        return render(request, "core/activacion.html", {
            "huella": huella_maquina(),
            "estado": estado_licencia(),
            "dias": dias_restantes(),
            "tipo": tipo_licencia_actual(),
        })

    def post(self, request):
        clave = request.POST.get("clave", "").strip().upper()

        # Intentar validar como perpetua primero, luego como anual
        if clave_valida(clave, "perpetua"):
            guardar_licencia("perpetua", clave)
            messages.success(request, "[OK] Licencia PERPETUA activada. Gracias!")
            return redirect("dashboard")

        if clave_valida(clave, "anual"):
            guardar_licencia("anual", clave)
            messages.success(request, "[OK] Licencia ANUAL activada por 1 anio. Gracias!")
            return redirect("dashboard")

        messages.error(request, "Clave de licencia invalida para esta maquina")
        return redirect("activacion")
