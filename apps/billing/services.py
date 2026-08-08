from decimal import Decimal

from django.db import transaction

from .models import DetalleFactura, Factura

# Solo se facturan exámenes que ya fueron realizados
ESTADOS_REALIZADOS = ["cargado", "validado", "publicado"]


def generar_factura(expediente, usuario, descuento=Decimal("0")):
    """
    Genera la factura de una orden tomando los exámenes realizados
    y congelando el precio vigente de cada examen al momento de facturar.
    """
    with transaction.atomic():
        if expediente.facturas.exclude(estado="anulada").exists():
            raise ValueError("Esta orden ya tiene una factura activa")

        realizados = (
            expediente.resultados.filter(estado__in=ESTADOS_REALIZADOS)
            .select_related("examen")
        )

        if not realizados.exists():
            raise ValueError("La orden aún no tiene exámenes realizados para facturar")

        ultima = Factura.objects.order_by("-id").first()
        numero = f"F-{(ultima.id + 1) if ultima else 1:06d}"

        factura = Factura.objects.create(
            numero=numero,
            expediente=expediente,
            descuento=descuento,
            creado_por=usuario,
        )

        subtotal = Decimal("0")
        for resultado in realizados:
            costo = resultado.examen.costo_actual
            precio = costo.precio if costo else Decimal("0")

            DetalleFactura.objects.create(
                factura=factura,
                examen=resultado.examen,
                cantidad=1,
                precio_unitario=precio,
                subtotal=precio,
            )
            subtotal += precio

        factura.subtotal = subtotal
        factura.total = max(subtotal - descuento, Decimal("0"))
        factura.save(update_fields=["subtotal", "total"])

        return factura
