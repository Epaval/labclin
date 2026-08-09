"""
Lanzador de Lab Clínico - Modo Escritorio
"""
import argparse
import os
import socket
import sys
import threading
import traceback

FROZEN = getattr(sys, "frozen", False)

# CRÍTICO: Forzar UTF-8 en Windows para evitar UnicodeEncodeError
# Esto resuelve problemas con símbolos como ✓, ✗, etc.
if sys.platform == "win32":
    try:
        # Python 3.7+
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    # Variable de entorno para Django/Python
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def exe_dir():
    if FROZEN:
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


EXE_DIR = exe_dir()

if FROZEN:
    DATA_BASE = os.environ.get(
        "LABCLIN_DATA",
        os.path.join(os.path.expanduser("~"), "LabClinico"),
    )
else:
    DATA_BASE = EXE_DIR

ERROR_LOG = os.path.join(DATA_BASE, "launcher_error.log")


def reportar_error(exc_texto):
    try:
        os.makedirs(DATA_BASE, exist_ok=True)
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(exc_texto + "\n")
    except Exception:
        pass

    print(exc_texto, file=sys.stderr)

    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Error al iniciar Lab Clínico:\n\n{exc_texto[:800]}\n\n"
            f"Detalle completo en:\n{ERROR_LOG}",
            "Lab Clínico - Error",
            0x10,
        )
    except Exception:
        pass


def main():
    if FROZEN:
        sys.path.insert(0, getattr(sys, "_MEIPASS", EXE_DIR))
    else:
        sys.path.insert(0, EXE_DIR)

    parser = argparse.ArgumentParser(description="Lab Clínico - Modo Escritorio")
    parser.add_argument("--lan", action="store_true")
    parser.add_argument("--puerto", type=int, default=8000)
    parser.add_argument("--sin-ventana", action="store_true")
    args = parser.parse_args()

    os.environ["LABCLIN_MODO"] = "escritorio"
    os.environ["LABCLIN_BASE"] = DATA_BASE
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
        print("  Lab Clínico disponible en la red local:")
        print(f"  → Esta PC:   {url}")
        print(f"  → Otras PCs: http://{ip}:{args.puerto}")
        print("=" * 60)

    if args.sin_ventana:
        print(f"Servidor activo en {url}  (Ctrl+C para salir)")
        import time
        while True:
            time.sleep(3600)

    import webview
    webview.create_window(
        "Lab Clínico", url,
        width=1360, height=860, min_size=(1024, 700),
    )
    webview.start()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        reportar_error(traceback.format_exc())
        sys.exit(1)
