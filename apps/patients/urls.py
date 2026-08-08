from django.urls import path

from .views import (
    EnviarReportePDFView,
    ExpedienteCreateView,
    ExpedienteDetailView,
    ExpedienteListView,
    PacienteCreateView,
    PacienteHistorialView,
    PacienteListView,
    PacienteReportePDFView,
    PacienteUpdateView,
)

app_name = "patients"

urlpatterns = [
    path("", PacienteListView.as_view(), name="list"),
    path("nuevo/", PacienteCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", PacienteUpdateView.as_view(), name="update"),

    path("<int:pk>/historial/", PacienteHistorialView.as_view(), name="historial"),
    path("<int:pk>/reporte/pdf/", PacienteReportePDFView.as_view(), name="reporte_pdf"),
    path("<int:pk>/reporte/enviar/", EnviarReportePDFView.as_view(), name="reporte_enviar"),

    path("ordenes/", ExpedienteListView.as_view(), name="orden_list"),
    path("ordenes/nueva/", ExpedienteCreateView.as_view(), name="orden_create"),
    path("ordenes/<int:pk>/", ExpedienteDetailView.as_view(), name="orden_detail"),
]
