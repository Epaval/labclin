from decimal import Decimal
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ExamenForm
from .models import CostoExamen, Examen


class ExamenListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Examen
    permission_required = "exams.view_examen"
    template_name = "exams/examen_list.html"
    context_object_name = "object_list"
    paginate_by = 6

    def get_queryset(self):
        qs = Examen.objects.order_by("perfil", "nombre_completo")

        q = self.request.GET.get("q", "").strip()

        if q:
            # Búsqueda inteligente multi-término sin acentos ni mayúsculas
            for term in q.split():
                qs = qs.filter(
                    Q(nombre_completo__unaccent__icontains=term)
                    | Q(perfil__unaccent__icontains=term)
                    | Q(valores_ref__unaccent__icontains=term)
                )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


class ExamenCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Examen
    form_class = ExamenForm
    permission_required = "exams.add_examen"
    template_name = "form.html"
    success_url = reverse_lazy("exams:list")
    extra_context = {"title": "Nuevo examen"}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["datalist_perfiles"] = sorted(
            {p for p in Examen.objects.values_list("perfil", flat=True).distinct() if p}
        )
        return ctx


class ExamenUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Examen
    form_class = ExamenForm
    permission_required = "exams.change_examen"
    template_name = "form.html"
    success_url = reverse_lazy("exams:list")
    extra_context = {"title": "Editar examen"}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["next"] = self.request.GET.get("next", "")
        ctx["datalist_perfiles"] = sorted(
            {p for p in Examen.objects.values_list("perfil", flat=True).distinct() if p}
        )
        return ctx

    def get_success_url(self):
        next_url = self.request.POST.get("next") or self.request.GET.get("next")
        if next_url and next_url.startswith("/"):
            return next_url
        return super().get_success_url()


class AjusteMasivoView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "exams/ajuste_masivo.html"
    permission_required = "exams.change_examen"

    def _preview(self, porcentaje):
        factor = Decimal(str(1 + porcentaje / 100))
        filas = []
        for ex in Examen.objects.filter(activo=True).order_by("nombre_completo"):
            actual = ex.precio_actual or Decimal("0")
            nuevo = (actual * factor).quantize(Decimal("0.01"))
            filas.append({"examen": ex, "actual": actual, "nuevo": nuevo})
        return filas

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_examenes"] = Examen.objects.filter(activo=True).count()
        return ctx

    def post(self, request, *args, **kwargs):
        try:
            porcentaje = float(request.POST.get("porcentaje", "0"))
        except ValueError:
            porcentaje = 0.0
        if request.POST.get("aplicar"):
            filas = [f for f in self._preview(porcentaje) if f["nuevo"] != f["actual"]]
            for fila in filas:
                CostoExamen.objects.create(examen=fila["examen"], precio=fila["nuevo"], activo=True)
            messages.success(request, f"Ajuste de {porcentaje:+.2f}% aplicado a {len(filas)} examenes")
            return redirect("exams:list")
        ctx = self.get_context_data()
        ctx["porcentaje"] = porcentaje
        ctx["preview"] = self._preview(porcentaje)
        return self.render_to_response(ctx)
