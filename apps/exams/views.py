from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ExamenForm
from .models import Examen


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


class ExamenUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Examen
    form_class = ExamenForm
    permission_required = "exams.change_examen"
    template_name = "form.html"
    success_url = reverse_lazy("exams:list")
    extra_context = {"title": "Editar examen"}
