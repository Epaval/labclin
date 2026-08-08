from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.doctors.models import Medico
from apps.exams.models import Examen
from apps.patients.models import Paciente
from apps.results.models import Resultado


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_pacientes"] = Paciente.objects.filter(activo=True).count()
        context["total_medicos"] = Medico.objects.filter(activo=True).count()
        context["total_examenes"] = Examen.objects.filter(activo=True).count()
        context["total_resultados"] = Resultado.objects.count()
        context["modo_escritorio"] = settings.ESCRITORIO
        return context
