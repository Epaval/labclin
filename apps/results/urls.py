from django.urls import path

from .views import ResultadoListView, ResultadoUpdateView, TestEmailView

app_name = "results"

urlpatterns = [
    path("", ResultadoListView.as_view(), name="list"),
    path("<int:pk>/cargar/", ResultadoUpdateView.as_view(), name="update"),
    path("test-email/", TestEmailView.as_view(), name="test_email"),
]
