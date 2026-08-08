"""
Compatibilidad SQLite para el modo escritorio.

Replica el comportamiento de `unaccent` de PostgreSQL registrando una
función SQL propia, y activa WAL para mejor concurrencia local.
"""
import unicodedata

from django.db.backends.signals import connection_created
from django.db.models import CharField, TextField, Transform


def _quitar_acentos(valor):
    if valor is None:
        return valor
    return "".join(
        ch for ch in unicodedata.normalize("NFD", str(valor))
        if unicodedata.category(ch) != "Mn"
    )


def _configurar_sqlite(sender, connection, **kwargs):
    if connection.vendor != "sqlite":
        return

    # Función UNACCENT disponible en SQL
    connection.connection.create_function(
        "UNACCENT", 1, _quitar_acentos, deterministic=True
    )

    # Mejor concurrencia para varios usuarios en red local
    cursor = connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")


class UnaccentSQLite(Transform):
    lookup_name = "unaccent"
    function = "UNACCENT"
    bilateral = True  # quita acentos también al término buscado


def instalar():
    from django.conf import settings

    if getattr(settings, "ESCRITORIO", False):
        connection_created.connect(_configurar_sqlite)
        CharField.register_lookup(UnaccentSQLite)
        TextField.register_lookup(UnaccentSQLite)
