import sqlite3
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse
from django.shortcuts import redirect
from django.views import View


class BackupView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Respaldo de un clic: crea la copia y la descarga (solo escritorio)"""

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser or user.has_perm("accounts.view_empleado")

    def get(self, request):
        if not settings.ESCRITORIO:
            messages.error(request, "El respaldo de un clic solo existe en modo escritorio")
            return redirect("dashboard")

        origen = settings.DATABASES["default"]["NAME"]

        dir_backups = settings.DATA_DIR / "backups"
        dir_backups.mkdir(parents=True, exist_ok=True)

        nombre = f"labclin_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        destino = dir_backups / nombre

        src = sqlite3.connect(str(origen))
        dst = sqlite3.connect(str(destino))
        with dst:
            src.backup(dst)
        src.close()
        dst.close()

        messages.success(request, f"Respaldo {nombre} creado y descargado")
        return FileResponse(open(destino, "rb"), as_attachment=True, filename=nombre)
