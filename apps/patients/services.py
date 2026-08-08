import io

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa


def generar_pdf_reporte(paciente, expedientes):
    """Genera el reporte de resultados del paciente en PDF"""
    html = render_to_string(
        "reports/reporte_resultados.html",
        {
            "paciente": paciente,
            "expedientes": expedientes,
            "fecha_generacion": timezone.now(),
        },
    )

    buffer = io.BytesIO()
    estado = pisa.CreatePDF(io.StringIO(html), dest=buffer, encoding="utf-8")

    if estado.err:
        raise ValueError("Error al generar el PDF del reporte")

    return buffer.getvalue()


def enviar_reporte_pdf(paciente, expedientes):
    """Envía el reporte PDF al correo del paciente"""
    if not paciente.email:
        raise ValueError("El paciente no tiene correo electrónico registrado")

    pdf = generar_pdf_reporte(paciente, expedientes)

    mensaje = EmailMessage(
        subject=f"Resultados de laboratorio - {paciente.full_name}",
        body=(
            f"Estimado(a) {paciente.full_name}:\n\n"
            "Adjunto encontrará el reporte de sus resultados de laboratorio.\n\n"
            "Este documento es confidencial.\n"
            "Laboratorio Clínico"
        ),
        to=[paciente.email],
    )
    mensaje.attach(
        f"resultados_{paciente.ci or paciente.pk}.pdf",
        pdf,
        "application/pdf",
    )
    mensaje.send(fail_silently=False)
