from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView

from .forms import ResultadoForm
from .models import Resultado


class ResultadoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Resultado
    permission_required = "results.view_resultado"
    template_name = "generic_list.html"
    context_object_name = "object_list"
    paginate_by = 20
    extra_context = {"title": "Resultados"}


class ResultadoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Resultado
    form_class = ResultadoForm
    permission_required = "results.editar_result"
    template_name = "results/resultado_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Cargar resultado: {self.object.examen.nombre_completo}"
        context["valores_ref"] = self.object.examen.valores_ref
        return context

    def form_valid(self, form):
        form.instance.actualizado_por = self.request.user

        if self.object.estado == "borrador" and self.object.tiene_resultado:
            form.instance.estado = "cargado"

        messages.success(self.request, "Resultado guardado correctamente")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "patients:orden_detail",
            kwargs={"pk": self.object.expediente_id},
        )


class TestEmailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "results.view_resultado"
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if not request.user.email:
            messages.error(request, "Tu usuario no tiene email configurado")
            return redirect("dashboard")

        try:
            send_mail(
                subject="Correo de prueba",
                message="Si ves este correo, la configuración básica de email funciona.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            messages.success(request, f"Correo de prueba enviado a {request.user.email}")
        except Exception as exc:
            messages.error(request, f"No se pudo enviar el correo: {exc}")

        return redirect("dashboard")
