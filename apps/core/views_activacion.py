from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from .licencias import (
    clave_valida,
    dias_prueba_restantes,
    estado_licencia,
    huella_maquina,
)
from django.conf import settings


class ActivacionView(View):
    def get(self, request):
        return render(request, "core/activacion.html", {
            "huella": huella_maquina(),
            "estado": estado_licencia(),
            "dias": dias_prueba_restantes(),
        })

    def post(self, request):
        clave = request.POST.get("clave", "")

        if clave_valida(clave):
            (settings.DATA_DIR / "licencia.key").write_text(clave.strip().upper())
            messages.success(request, "✅ Licencia activada correctamente. ¡Gracias!")
            return redirect("dashboard")

        messages.error(request, "Clave de licencia inválida para esta máquina")
        return redirect("activacion")
