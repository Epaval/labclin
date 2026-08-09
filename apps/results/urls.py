from django.urls import path

from .views_atendidos import HistoriaPacienteView, PacientesAtendidosView
from .views import ResultadoListView, ResultadoUpdateView, TestEmailView

app_name = "results"

urlpatterns = [
    path("", PacientesAtendidosView.as_view(), name="pacientes_atendidos"),
    path("historia/<int:pk>/", HistoriaPacienteView.as_view(), name="historia"),
    path("lista/", ResultadoListView.as_view(), name="list"),
    path("<int:pk>/cargar/", ResultadoUpdateView.as_view(), name="update"),
    path("test-email/", TestEmailView.as_view(), name="test_email"),
]
