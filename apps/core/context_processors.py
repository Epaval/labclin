from django.utils.safestring import mark_safe


def tunnel_context(request):
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
            ctx["tunnel_qr"] = mark_safe(qr)
        return ctx
    except Exception:
        return {}
