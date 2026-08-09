from django.db import models


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

    @classmethod
    def cargar(cls):
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create()
        return obj
