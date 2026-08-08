"""
Lanzador de Lab Clínico - Modo Escritorio

Uso:
    python desktop/launcher.py                     → ventana nativa (1 PC)
    python desktop/launcher.py --lan               → ventana + acceso desde otras PCs
    python desktop/launcher.py --sin-ventana       → solo servidor (abres navegador tú)
    python desktop/launcher.py --puerto 8010       → puerto personalizado
"""
import argparse
import os
import socket
import sys
import threading


def base_path():
    # Empaquetado con PyInstaller → carpeta del .exe
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # Desarrollo → raíz del proyecto
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE = base_path()

# CRÍTICO: Agregar la raíz al path de Python ANTES de importar Django
sys.path.insert(0, BASE)

parser = argparse.ArgumentParser(description="Lab Clínico - Modo Escritorio")
parser.add_argument("--lan", action="store_true",
                    help="Permitir conexiones de otras PCs de la red local")
parser.add_argument("--puerto", type=int, default=8000)
parser.add_argument("--sin-ventana", action="store_true",
                    help="Correr solo el servidor, sin ventana nativa")
args = parser.parse_args()

# Modo escritorio ANTES de importar Django
os.environ["LABCLIN_MODO"] = "escritorio"
os.environ["LABCLIN_BASE"] = BASE
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

# Migraciones automáticas al abrir (crea/actualiza la BD sin tocar nada)
from django.core.management import call_command

call_command("migrate", interactive=False, verbosity=0)

# Servidor embebido (Waitress) en un hilo
host = "0.0.0.0" if args.lan else "127.0.0.1"

from waitress import serve
from django.core.wsgi import get_wsgi_application

threading.Thread(
    target=serve,
    kwargs={"app": get_wsgi_application(), "host": host,
            "port": args.puerto, "threads": 8},
    daemon=True,
).start()

url = f"http://127.0.0.1:{args.puerto}"

if args.lan:
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        ip = "TU_IP"
    print("=" * 60)
    print("  Lab Clínico está disponible en la red local:")
    print(f"  → Esta PC:      {url}")
    print(f"  → Otras PCs:    http://{ip}:{args.puerto}")
    print("=" * 60)

if args.sin_ventana:
    print(f"Servidor activo en {url}  (Ctrl+C para salir)")
    import time
    while True:
        time.sleep(3600)

# Ventana nativa de escritorio
import webview

webview.create_window(
    "Lab Clínico",
    url,
    width=1360,
    height=860,
    min_size=(1024, 700),
)
webview.start()
