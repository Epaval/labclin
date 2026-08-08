from django.conf import settings
from django.shortcuts import redirect

from .licencias import estado_licencia


class LicenciaMiddleware:
    """En modo escritorio, bloquea la app si la licencia está vencida"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.ESCRITORIO:
            rutas_libres = (
                "/activacion",
                "/static",
                "/favicon",
            )
            if estado_licencia() == "vencida" and not request.path.startswith(rutas_libres):
                return redirect("activacion")

        return self.get_response(request)
