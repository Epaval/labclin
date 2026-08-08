from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone


class Paciente(models.Model):
    SEXO_CHOICES = [
        ("F", "Femenino"),
        ("M", "Masculino"),
        ("O", "Otro"),
    ]

    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120)

    ci = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="CI",
    )

    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fecha_nac = models.DateField(verbose_name="Fecha de nacimiento")

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_fecha_act = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "paciente"
        permissions = [
            ("crear_paciente", "Crear paciente"),
        ]
        constraints = [
            UniqueConstraint(
                Lower("ci"),
                condition=Q(ci__isnull=False),
                name="paciente_ci_lower_unique",
            ),
            UniqueConstraint(
                Lower("telefono"),
                condition=Q(telefono__isnull=False),
                name="paciente_telefono_lower_unique",
            ),
            UniqueConstraint(
                Lower("email"),
                condition=Q(email__isnull=False),
                name="paciente_email_lower_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["apellidos", "nombres"]),
            models.Index(fields=["ci"]),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.nombres} {self.apellidos}".strip()

    @property
    def edad(self):
        if not self.fecha_nac:
            return None

        hoy = timezone.localdate()

        if self.fecha_nac > hoy:
            return 0

        anos = hoy.year - self.fecha_nac.year

        if (hoy.month, hoy.day) < (self.fecha_nac.month, self.fecha_nac.day):
            anos -= 1

        return anos

    def clean(self):
        super().clean()
        if self.fecha_nac and self.fecha_nac > timezone.localdate():
            raise ValidationError({
                "fecha_nac": "La fecha de nacimiento no puede ser futura"
            })

    def save(self, *args, **kwargs):
        self.email = self.email.lower() if self.email else None

        if self.telefono:
            self.telefono = "".join(
                ch for ch in self.telefono if ch.isdigit() or ch == "+"
            )
        else:
            self.telefono = None

        self.ci = self.ci.strip() if self.ci else None

        super().save(*args, **kwargs)


class Expediente(models.Model):
    ESTADO_CHOICES = [
        ("abierto", "Abierto"),
        ("procesando", "Procesando"),
        ("cerrado", "Cerrado"),
        ("anulado", "Anulado"),
    ]

    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="expedientes",
    )

    bioanalista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="expedientes_asignados",
        limit_choices_to={"rol__nombre": "bioanalista", "is_active": True},
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="expedientes_creados",
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="abierto",
    )

    observaciones = models.TextField(blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_fecha_act = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "expediente"
        permissions = [
            ("crear_orden_lab", "Crear orden de laboratorio"),
        ]
        indexes = [
            models.Index(fields=["paciente", "estado"]),
            models.Index(fields=["fecha_creacion"]),
        ]

    def __str__(self):
        return f"Expediente {self.pk} - {self.paciente}"


class ExpedienteMedico(models.Model):
    expediente = models.ForeignKey(
        Expediente,
        on_delete=models.CASCADE,
        related_name="expedientes_medicos",
    )
    medico = models.ForeignKey(
        "doctors.Medico",
        on_delete=models.CASCADE,
        related_name="expedientes_medicos",
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = "expediente_medico"
        constraints = [
            UniqueConstraint(
                fields=["expediente", "medico"],
                name="uniq_expediente_medico",
            ),
        ]

    def __str__(self):
        return f"{self.expediente} - {self.medico}"


class Resumen(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name="resumenes",
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="resumenes_creados",
    )

    titulo = models.CharField(max_length=255)
    observacion = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_fecha_act = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resumen"

    def __str__(self):
        return f"Resumen {self.pk} - {self.paciente}"


class ResumenDetalle(models.Model):
    resumen = models.ForeignKey(
        Resumen,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    resultado = models.ForeignKey(
        "results.Resultado",
        on_delete=models.PROTECT,
        related_name="resumen_detalles",
    )

    class Meta:
        db_table = "resumen_detalle"
        constraints = [
            UniqueConstraint(
                fields=["resumen", "resultado"],
                name="uniq_resumen_resultado",
            ),
        ]

    def __str__(self):
        return f"{self.resumen} - {self.resultado}"
