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
