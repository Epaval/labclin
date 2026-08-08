"""
Lanzador de Lab Clínico - Modo Escritorio
"""
import argparse
import os
import socket
import sys
import threading

FROZEN = getattr(sys, "frozen", False)


def exe_dir():
    if FROZEN:
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


EXE_DIR = exe_dir()

# CRÍTICO: en el exe, el código vive dentro del bundle (_internal).
# En desarrollo, en la raíz del proyecto.
if FROZEN:
    sys.path.insert(0, getattr(sys, "_MEIPASS", EXE_DIR))
else:
    sys.path.insert(0, EXE_DIR)

parser = argparse.ArgumentParser(description="Lab Clínico - Modo Escritorio")
parser.add_argument("--lan", action="store_true",
                    help="Permitir conexiones de otras PCs de la red local")
parser.add_argument("--puerto", type=int, default=8000)
parser.add_argument("--sin-ventana", action="store_true",
                    help="Correr solo el servidor, sin ventana nativa")
args = parser.parse_args()

# Datos en carpeta ESCRIBIBLE (Program Files no lo es):
# instalado → C:\Users\<usuario>\LabClinico ; desarrollo → raíz del proyecto
if FROZEN:
    data_base = os.environ.get(
        "LABCLIN_DATA",
        os.path.join(os.path.expanduser("~"), "LabClinico"),
    )
else:
    data_base = EXE_DIR

os.environ["LABCLIN_MODO"] = "escritorio"
os.environ["LABCLIN_BASE"] = data_base
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.core.management import call_command

call_command("migrate", interactive=False, verbosity=0)

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

import webview

webview.create_window(
    "Lab Clínico",
    url,
    width=1360,
    height=860,
    min_size=(1024, 700),
)
webview.start()
