"""
HERRAMIENTA DEL VENDEDOR - generar clave desde la huella del cliente.

Uso:  python tools/generar_licencia.py 9F3A21BC7D4E60C1
"""
import hashlib
import hmac
import sys

# ⚠️ Debe coincidir con apps/core/licencias.py
SECRET = b"AZMA1972JCPD1970#2005$1991"

if len(sys.argv) != 2:
    print("Uso: python generar_licencia.py <HUELLA>")
    sys.exit(1)

huella = sys.argv[1].strip().upper()
clave = hmac.new(SECRET, huella.encode(), hashlib.sha256).hexdigest()[:12].upper()
print(f"Huella: {huella}")
print(f"CLAVE : {clave}")
