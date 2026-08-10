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
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
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
ESTACION_CFG = os.path.join(DATA_BASE, "estacion.cfg")


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


def pedir_ip_servidor(ip_actual=""):
    """Asistente gráfico para pedir la IP del servidor (modo estación)"""
    import tkinter as tk
    from tkinter import ttk, messagebox

    resultado = {"ip": None}

    root = tk.Tk()
    root.title("Lab Clínico - Conectar al servidor")
    root.geometry("460x320")
    root.resizable(False, False)
    root.configure(bg="#f8fafc")

    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    # Frame principal
    frame = tk.Frame(root, bg="#f8fafc", padx=30, pady=25)
    frame.pack(fill="both", expand=True)

    # Título
    titulo = tk.Label(
        frame, text="Lab Clínico",
        font=("Segoe UI", 20, "bold"),
        bg="#f8fafc", fg="#0f172a",
    )
    titulo.pack(pady=(0, 5))

    subtitulo = tk.Label(
        frame, text="Conectar como estación",
        font=("Segoe UI", 11),
        bg="#f8fafc", fg="#64748b",
    )
    subtitulo.pack(pady=(0, 20))

    # Etiqueta
    label = tk.Label(
        frame, text="IP del servidor (PC del laboratorio):",
        font=("Segoe UI", 10, "bold"),
        bg="#f8fafc", fg="#334155",
        anchor="w",
    )
    label.pack(fill="x", pady=(0, 5))

    # Campo de entrada
    entry_ip = ttk.Entry(frame, font=("Consolas", 13))
    entry_ip.insert(0, ip_actual)
    entry_ip.pack(fill="x", ipady=6, pady=(0, 20))
    entry_ip.focus_set()

    def conectar():
        ip = entry_ip.get().strip()
        if not ip:
            messagebox.showwarning("Atención", "Ingresa la IP del servidor")
            return
        resultado["ip"] = ip
        root.destroy()

    def cancelar():
        resultado["ip"] = None
        root.destroy()

    # Frame de botones con altura fija
    btn_frame = tk.Frame(frame, bg="#f8fafc")
    btn_frame.pack(fill="x", pady=(0, 15))
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    btn_cancelar = tk.Button(
        btn_frame, text="Cancelar", command=cancelar,
        font=("Segoe UI", 10),
        bg="#e2e8f0", fg="#334155",
        activebackground="#cbd5e1",
        relief="flat",
        padx=20, pady=10,
        cursor="hand2",
    )
    btn_cancelar.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    btn_conectar = tk.Button(
        btn_frame, text="Conectar", command=conectar,
        font=("Segoe UI", 10, "bold"),
        bg="#0ea5e9", fg="white",
        activebackground="#0284c7", activeforeground="white",
        relief="flat",
        padx=20, pady=10,
        cursor="hand2",
    )
    btn_conectar.grid(row=0, column=1, sticky="ew", padx=(8, 0))

    # Enter para conectar
    entry_ip.bind("<Return>", lambda e: conectar())

    # Nota al pie
    nota = tk.Label(
        frame,
        text="Pregunta la IP al laboratorio principal.\nSe guardará para no volver a pedirla.",
        font=("Segoe UI", 8),
        bg="#f8fafc", fg="#94a3b8",
        justify="center",
    )
    nota.pack(fill="x", pady=(5, 0))

    # Ajustar la ventana al contenido real (respetando escalado del sistema)
    root.update_idletasks()
    req_w = max(root.winfo_reqwidth() + 20, 460)
    req_h = max(root.winfo_reqheight() + 20, 340)
    root.geometry(f"{req_w}x{req_h}")
    try:
        root.eval("tk::PlaceWindow . center")
    except Exception:
        pass

    root.protocol("WM_DELETE_WINDOW", cancelar)
    root.mainloop()

    return resultado["ip"]


def leer_ip_guardada():
    try:
        return open(ESTACION_CFG, "r", encoding="utf-8").read().strip()
    except Exception:
        return ""


def guardar_ip(ip):
    try:
        os.makedirs(os.path.dirname(ESTACION_CFG), exist_ok=True)
        with open(ESTACION_CFG, "w", encoding="utf-8") as f:
            f.write(ip)
    except Exception:
        pass


def abrir_ventana(url, mantener_vivo=False):
    """Abre la app en ventana nativa; si no hay GUI, usa el navegador"""
    try:
        import webview
        webview.create_window(
            "Lab Clínico", url,
            width=1360, height=860, min_size=(1024, 700),
        )
        webview.start()
    except Exception:
        import webbrowser
        print(f"[i] Sin GUI nativa: abriendo navegador en {url}")
        webbrowser.open(url)
        if mantener_vivo and not FROZEN:
            import time
            while True:
                time.sleep(3600)


def main():
    if FROZEN:
        sys.path.insert(0, getattr(sys, "_MEIPASS", EXE_DIR))
    else:
        sys.path.insert(0, EXE_DIR)

    parser = argparse.ArgumentParser(description="Lab Clínico - Modo Escritorio")
    parser.add_argument("--lan", action="store_true")
    parser.add_argument("--puerto", type=int, default=8000)
    parser.add_argument("--sin-ventana", action="store_true")
    parser.add_argument(
        "--conectar", nargs="?", const="pedir", metavar="IP_PUERTO",
        help="Modo estacion. Sin argumento: pide la IP. Con argumento: conecta directo.",
    )
    args = parser.parse_args()

    # Modo estacion: conectar al servidor
    if args.conectar is not None:
        ip_puerto = args.conectar

        if ip_puerto == "pedir":
            ip_puerto = leer_ip_guardada()
            if not ip_puerto:
                ip_puerto = pedir_ip_servidor()
                if not ip_puerto:
                    sys.exit(0)
                guardar_ip(ip_puerto)

        url = ip_puerto
        if not url.startswith("http"):
            url = "http://" + url

        abrir_ventana(url)
        sys.exit(0)

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

    abrir_ventana(url, mantener_vivo=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        reportar_error(traceback.format_exc())
        sys.exit(1)
