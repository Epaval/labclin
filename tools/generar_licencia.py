"""
HERRAMIENTA DEL VENDEDOR - Generar claves de licencia

Uso:
  python tools/generar_licencia.py HUELLA              -> perpetua
  python tools/generar_licencia.py HUELLA anual        -> anual (1 anio)
  python tools/generar_licencia.py HUELLA perpetua     -> perpetua
"""
import hashlib
import hmac
import sys

SECRET = b"LABCLIN-SECRETO-2026-CAMBIA-ESTO"

if len(sys.argv) < 2:
    print("Uso: python generar_licencia.py HUELLA [anual|perpetua]")
    sys.exit(1)

huella = sys.argv[1].strip().upper()
tipo = sys.argv[2].strip().lower() if len(sys.argv) > 2 else "perpetua"

if tipo not in ["anual", "perpetua"]:
    print(f"Tipo invalido: {tipo}. Use 'anual' o 'perpetua'")
    sys.exit(1)

mensaje = f"{huella}|{tipo}"
clave = hmac.new(SECRET, mensaje.encode(), hashlib.sha256).hexdigest()[:12].upper()

print(f"Huella:  {huella}")
print(f"Tipo:    {tipo}")
print(f"CLAVE:   {clave}")
print()
print("El cliente debe escribir esta clave en la pantalla de activacion.")
