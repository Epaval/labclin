"""
Licencias offline para el modo escritorio.

Flujo:
  1. La app muestra su HUELLA (código de máquina).
  2. El vendedor genera una CLAVE a partir de esa huella.
  3. La clave se guarda en data/licencia.key y se valida offline.
"""
import hashlib
import hmac
import platform
import uuid
from datetime import datetime

# ⚠️ SECRETO DEL VENDEDOR: cámbialo y NO lo compartas.
# Debe ser idéntico en la app y en tools/generar_licencia.py
SECRET = b"AZMA1972JCPD1970#2005$1991"

PRUEBA_DIAS = 15


def huella_maquina() -> str:
    """Identificador único de la PC (MAC + nombre de equipo)"""
    base = f"{uuid.getnode()}|{platform.node().lower()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16].upper()


def generar_clave(huella: str) -> str:
    """Herramienta del vendedor: huella → clave de activación"""
    return (
        hmac.new(SECRET, huella.strip().upper().encode(), hashlib.sha256)
        .hexdigest()[:12]
        .upper()
    )


def clave_valida(clave: str) -> bool:
    return hmac.compare_digest(clave.strip().upper(), generar_clave(huella_maquina()))


def estado_licencia() -> str:
    """Devuelve: 'activada' | 'prueba' | 'vencida'"""
    from django.conf import settings

    lic_file = settings.DATA_DIR / "licencia.key"
    if lic_file.exists():
        if clave_valida(lic_file.read_text().strip()):
            return "activada"

    # Periodo de prueba desde la primera ejecución
    prueba_file = settings.DATA_DIR / "primera_ejecucion"
    if not prueba_file.exists():
        prueba_file.write_text(datetime.now().isoformat())

    inicio = datetime.fromisoformat(prueba_file.read_text().strip())
    if (datetime.now() - inicio).days <= PRUEBA_DIAS:
        return "prueba"

    return "vencida"


def dias_prueba_restantes() -> int:
    from django.conf import settings

    prueba_file = settings.DATA_DIR / "primera_ejecucion"
    if not prueba_file.exists():
        return PRUEBA_DIAS
    inicio = datetime.fromisoformat(prueba_file.read_text().strip())
    return max(PRUEBA_DIAS - (datetime.now() - inicio).days, 0)
