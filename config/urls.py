from apps.core.views import BackupView
from apps.core.views_activacion import ActivacionView
from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import DashboardView
from . import views as error_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("respaldo/", BackupView.as_view(), name="backup"),
    path("activacion/", ActivacionView.as_view(), name="activacion"),
    path("accounts/", include("apps.accounts.urls")),
    path("pacientes/", include("apps.patients.urls")),
    path("medicos/", include("apps.doctors.urls")),
    path("examenes/", include("apps.exams.urls")),
    path("resultados/", include("apps.results.urls")),
    path("facturas/", include("apps.billing.urls")),
]

# Handlers personalizados de errores
handler403 = "config.views.handler403"
handler404 = "config.views.handler404"
handler500 = "config.views.handler500"
