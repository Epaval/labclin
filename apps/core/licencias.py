"""
Sistema de licencias con tipos:
  - prueba:   15 dias desde la primera ejecucion
  - anual:    1 anio desde la activacion
  - perpetua: para siempre
"""
import hashlib
import hmac
import platform
import uuid
from datetime import datetime, timedelta

# SECRETO DEL VENDEDOR (cambialo y no lo compartas)
SECRET = b"AZMA1972JCPD1970#2005$1991"

PRUEBA_DIAS = 7
ANUAL_DIAS = 365

TIPOS_VALIDOS = ["anual", "perpetua"]


def huella_maquina() -> str:
    """Identificador unico de la PC"""
    base = f"{uuid.getnode()}|{platform.node().lower()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16].upper()


def generar_clave(huella: str, tipo: str = "perpetua") -> str:
    """Genera clave de activacion segun tipo de licencia"""
    if tipo not in TIPOS_VALIDOS:
        tipo = "perpetua"
    mensaje = f"{huella.strip().upper()}|{tipo}"
    return hmac.new(SECRET, mensaje.encode(), hashlib.sha256).hexdigest()[:12].upper()


def clave_valida(clave: str, tipo: str) -> bool:
    """Valida una clave para un tipo especifico"""
    esperada = generar_clave(huella_maquina(), tipo)
    return hmac.compare_digest(clave.strip().upper(), esperada)


def leer_licencia():
    """Lee el archivo de licencia. Devuelve (tipo, clave, fecha_activacion) o None"""
    from django.conf import settings

    lic_file = settings.DATA_DIR / "licencia.key"
    if not lic_file.exists():
        return None

    try:
        contenido = lic_file.read_text().strip()
        partes = contenido.split("|")
        if len(partes) == 3:
            tipo, clave, fecha_iso = partes
            fecha = datetime.fromisoformat(fecha_iso)
            return tipo, clave, fecha
        # Formato viejo (solo clave) -> tratar como perpetua
        return "perpetua", contenido, None
    except Exception:
        return None


def guardar_licencia(tipo: str, clave: str):
    """Guarda la licencia activada"""
    from django.conf import settings

    lic_file = settings.DATA_DIR / "licencia.key"
    fecha = datetime.now().isoformat()
    lic_file.write_text(f"{tipo}|{clave.strip().upper()}|{fecha}")


def estado_licencia() -> str:
    """
    Devuelve: 'activada' | 'prueba' | 'vencida'
    """
    from django.conf import settings

    licencia = leer_licencia()

    if licencia:
        tipo, clave, fecha_activacion = licencia

        # Validar la clave
        if clave_valida(clave, tipo):
            if tipo == "perpetua":
                return "activada"
            elif tipo == "anual":
                if fecha_activacion:
                    vencimiento = fecha_activacion + timedelta(days=ANUAL_DIAS)
                    if datetime.now() < vencimiento:
                        return "activada"
                    else:
                        return "vencida"
                return "activada"

    # Periodo de prueba
    prueba_file = settings.DATA_DIR / "primera_ejecucion"
    if not prueba_file.exists():
        prueba_file.write_text(datetime.now().isoformat())

    inicio = datetime.fromisoformat(prueba_file.read_text().strip())
    if (datetime.now() - inicio).days <= PRUEBA_DIAS:
        return "prueba"

    return "vencida"


def dias_restantes() -> int:
    """Dias restantes de licencia o prueba"""
    from django.conf import settings

    licencia = leer_licencia()
    if licencia:
        tipo, clave, fecha_activacion = licencia
        if clave_valida(clave, tipo):
            if tipo == "perpetua":
                return 99999
            elif tipo == "anual" and fecha_activacion:
                vencimiento = fecha_activacion + timedelta(days=ANUAL_DIAS)
                restante = (vencimiento - datetime.now()).days
                return max(restante, 0)

    prueba_file = settings.DATA_DIR / "primera_ejecucion"
    if not prueba_file.exists():
        return PRUEBA_DIAS
    inicio = datetime.fromisoformat(prueba_file.read_text().strip())
    return max(PRUEBA_DIAS - (datetime.now() - inicio).days, 0)


def tipo_licencia_actual() -> str:
    """Devuelve el tipo de licencia actual: prueba, anual, perpetua, vencida"""
    estado = estado_licencia()
    if estado == "prueba":
        return "prueba"
    if estado == "vencida":
        return "vencida"

    licencia = leer_licencia()
    if licencia:
        return licencia[0]
    return "prueba"
