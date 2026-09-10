from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def wa_link(examen):
    """Recibe un Resultado/Examen y devuelve un boton wa.me con el telefono del paciente."""
    from apps.core.models import ConfiguracionClinica
    from apps.core.whatsapp import armar_link_wa, renderizar_plantilla
    cfg = ConfiguracionClinica.cargar()
    try:
        pac = examen.expediente.paciente
    except Exception:
        return mark_safe('<span class="opacity-40 text-xs" title="Sin expediente">📲</span>')
    tel = (getattr(pac, "telefono", "") or "").strip()
    if not tel:
        return mark_safe('<span class="opacity-40 text-xs" title="Paciente sin telefono">📲</span>')
    nombre = f"{pac.nombres} {pac.apellidos}".strip()
    servicio = getattr(examen, "tipo_examen", None) or getattr(examen, "motivo", "") or "su resultado"
    msg = renderizar_plantilla(cfg.plantilla_whatsapp, nombre=nombre, clinica=cfg.nombre_clinica,
                               servicio=str(servicio), fecha=examen.fecha.strftime("%d/%m/%Y") if hasattr(examen, "fecha") else "",
                               hora=examen.fecha.strftime("%H:%M") if hasattr(examen, "fecha") else "")
    url = armar_link_wa(tel, msg, cfg.wa_prefijo)
    return mark_safe(
        f'<a href="{escape(url)}" target="_blank" rel="noopener" title="Notificar a {escape(nombre)}" '
        f'class="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs font-bold">📲 Notificar</a>')
