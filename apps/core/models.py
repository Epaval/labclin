import os

from django.core.exceptions import ValidationError
from django.db import models


def validar_logo(value):
    ext = value.name.rsplit(".", 1)[-1].lower()
    if ext not in ("png", "jpg", "jpeg", "svg"):
        raise ValidationError("Formato permitido: PNG, JPG o SVG")


class DatosLaboratorio(models.Model):
    """Datos del laboratorio para encabezados de PDF (registro unico)"""

    nombre = models.CharField(max_length=150, default="LAB CLINICO")
    rif = models.CharField("RIF", max_length=30, blank=True)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    ciudad = models.CharField(max_length=80, blank=True)
    lema = models.CharField(max_length=120, blank=True)
    simbolo_moneda = models.CharField(max_length=5, default="Bs.")
    logo = models.FileField(
        "Logo del laboratorio (PNG, JPG o SVG)",
        upload_to="logo/",
        null=True,
        blank=True,
        validators=[validar_logo],
        help_text="Se muestra en el encabezado de reportes y facturas en PDF",
    )
    bioanalista_nombre = models.CharField(
        "Bioanalista para firma", max_length=120, blank=True
    )
    bioanalista_registro = models.CharField(
        "Nro de registro del bioanalista", max_length=40, blank=True
    )

    class Meta:
        verbose_name = "Datos del laboratorio"
        verbose_name_plural = "Datos del laboratorio"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def logo_pdf_path(self):
        """Ruta util para el PDF: convierte SVG a PNG cacheado si es necesario"""
        if not self.logo:
            return None
        path = self.logo.path
        if path.lower().endswith(".svg"):
            png = path + ".png"
            if not os.path.exists(png) or os.path.getmtime(png) < os.path.getmtime(path):
                try:
                    from svglib.svglib import svg2rlg
                    from reportlab.graphics import renderPM
                    drawing = svg2rlg(path)
                    if drawing:
                        renderPM.drawToFile(drawing, png, fmt="PNG", dpi=150)
                except Exception:
                    return None
            return png if os.path.exists(png) else None
        return path

    @classmethod
    def cargar(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj
