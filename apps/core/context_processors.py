from django.core.cache import cache


def tasa_actual(request):
    t = cache.get("tasa_actual_cp")
    if t is None:
        from .models import TasaCambio
        t = TasaCambio.actual()
        cache.set("tasa_actual_cp", t, 60)
    return {"tasa_actual": t}


def tunnel_context(request):
    try:
        from apps.core.tunnel import tunnel_status
        return {"tunnel": tunnel_status()}
    except Exception:
        return {}


def tunnel_context(request):
    """Estado del tunel + QR para el banner del dashboard."""
    try:
        from apps.core.tunnel import tunnel_status
        st = tunnel_status()
        ctx = {"tunnel": st}
        if st.get("url"):
            from django.core.cache import cache
            qr = cache.get("tunnel_qr_svg")
            if not qr:
                import io, qrcode, qrcode.image.svg
                img = qrcode.make(st["url"], image_factory=qrcode.image.svg.SvgPathImage)
                buf = io.BytesIO()
                img.save(buf)
                qr = buf.getvalue().decode()
                cache.set("tunnel_qr_svg", qr, 3600)
            from django.utils.safestring import mark_safe
            ctx["tunnel_qr"] = mark_safe(qr)
        return ctx
    except Exception:
        return {}
