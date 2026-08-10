"""
Compatibilidad de busqueda sin acentos para SQLite (modo escritorio).

Registra la funcion SQL `unaccent` en conexiones SQLite y el lookup
`unaccent` para CharField/TextField. En PostgreSQL genera el mismo SQL
que django.contrib.postgres, asi que ambos modos quedan cubiertos.
"""
import unicodedata

from django.db.backends.signals import connection_created
from django.db.models import CharField, TextField
from django.db.models.lookups import Transform


def _quitar_acentos(valor):
    if valor is None:
        return None
    return "".join(
        c for c in unicodedata.normalize("NFD", str(valor))
        if unicodedata.category(c) != "Mn"
    )


def _registrar_funciones_sqlite(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.connection.create_function("unaccent", 1, _quitar_acentos)
        # Modo WAL + espera: varias estaciones trabajando sin "database locked"
        cursor = connection.connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")


class Unaccent(Transform):
    function = "unaccent"
    lookup_name = "unaccent"
    bilateral = True


def registrar():
    connection_created.connect(_registrar_funciones_sqlite)
    CharField.register_lookup(Unaccent)
    TextField.register_lookup(Unaccent)
