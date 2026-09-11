"""Monitor del tunel Cloudflare con cache de 5 min (sin dependencias externas)."""
import subprocess, sys, time, urllib.request
from django.conf import settings
from django.core.cache import cache


def _proceso_corriendo():
    try:
        if sys.platform == "win32":
            out = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq cloudflared.exe"],
                capture_output=True, text=True, timeout=5,
                creationflags=0x08000000,
            ).stdout
            return "cloudflared.exe" in out
        return subprocess.run(["pgrep", "-f", "cloudflared"],
                              capture_output=True, timeout=5).returncode == 0
    except Exception:
        return False


def tunnel_status(force=False):
    url = getattr(settings, "TUNNEL_URL", None)
    if not url:
        return {"estado": "desactivado", "url": "", "proc": False, "remoto": False, "ts": 0}
    data = cache.get("tunnel_status")
    if data and not force and time.time() - data.get("ts", 0) < 300:
        return data
    proc = _proceso_corriendo()
    remoto = False
    try:
        req = urllib.request.Request(url + "/accounts/login/",
                                     headers={"User-Agent": "tunnel-monitor"})
        with urllib.request.urlopen(req, timeout=8) as r:
            remoto = 200 <= r.status < 400
    except Exception:
        remoto = False
    if proc and remoto:
        estado = "activo"
    elif not proc:
        estado = "proceso_caido"
    else:
        estado = "sin_respuesta"
    data = {"estado": estado, "url": url, "proc": proc, "remoto": remoto, "ts": time.time()}
    cache.set("tunnel_status", data, 300)
    return data
