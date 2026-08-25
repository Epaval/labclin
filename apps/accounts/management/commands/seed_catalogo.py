import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.exams.models import CostoExamen, Examen, Perfil

# Lista completa de exámenes (idéntica a seed_datos pero aislada)
EXAMENES = [
    # Hematología
    ("Hematología completa", "Hematología", "Hemoglobina: 12-16 g/dL (M), 13-17 g/dL (H). Leucocitos: 4500-11000/mm³. Plaquetas: 150000-450000/mm³."),
    ("Hemoglobina", "Hematología", "Mujeres: 12-16 g/dL. Hombres: 13-17 g/dL."),
    ("Hematocrito", "Hematología", "Mujeres: 36-46%. Hombres: 41-53%."),
    ("Plaquetas", "Hematología", "150.000 - 450.000 /mm³"),
    ("Leucocitos", "Hematología", "4.500 - 11.000 /mm³"),
    ("Velocidad de sedimentación (VSG)", "Hematología", "Hombres: 0-15 mm/h. Mujeres: 0-20 mm/h."),
    ("Tiempo de Protrombina (TP)", "Coagulación", "11-13.5 segundos. INR: 0.8-1.2"),
    ("Tiempo de Tromboplastina Parcial (TTP)", "Coagulación", "25-35 segundos"),
    # Química sanguínea
    ("Glucosa en ayunas", "Química Sanguínea", "70-100 mg/dL. Prediabetes: 100-125. Diabetes: ≥126."),
    ("Urea", "Química Sanguínea", "15-45 mg/dL"),
    ("Creatinina", "Química Sanguínea", "Mujeres: 0.6-1.1 mg/dL. Hombres: 0.7-1.3 mg/dL."),
    ("Ácido úrico", "Química Sanguínea", "Mujeres: 2.4-6.0 mg/dL. Hombres: 3.4-7.0 mg/dL."),
    ("Colesterol total", "Perfil Lipídico", "Deseable: <200 mg/dL. Límite: 200-239. Alto: ≥240."),
    ("HDL", "Perfil Lipídico", "Hombres: >40 mg/dL. Mujeres: >50 mg/dL."),
    ("LDL", "Perfil Lipídico", "Óptimo: <100 mg/dL. Casi óptimo: 100-129."),
    ("Triglicéridos", "Perfil Lipídico", "Normal: <150 mg/dL. Límite: 150-199. Alto: 200-499."),
    # Hepáticas
    ("Bilirrubina total", "Hepáticas", "0.1-1.2 mg/dL"),
    ("Bilirrubina directa", "Hepáticas", "0.0-0.3 mg/dL"),
    ("TGO (AST)", "Hepáticas", "5-40 U/L"),
    ("TGP (ALT)", "Hepáticas", "7-56 U/L"),
    ("Fosfatasa alcalina", "Hepáticas", "44-147 U/L"),
    ("Proteínas totales", "Hepáticas", "6.0-8.3 g/dL"),
    ("Albúmina", "Hepáticas", "3.5-5.5 g/dL"),
    # Electrolitos
    ("Calcio", "Electrolitos", "8.5-10.5 mg/dL"),
    ("Fósforo", "Electrolitos", "2.5-4.5 mg/dL"),
    ("Sodio", "Electrolitos", "135-145 mEq/L"),
    ("Potasio", "Electrolitos", "3.5-5.0 mEq/L"),
    ("Cloro", "Electrolitos", "98-107 mEq/L"),
    # Hormonas y otros
    ("Uroanálisis completo", "Uroanálisis", "pH: 4.5-8.0. Densidad: 1.005-1.030. Sin proteínas, glucosa ni sangre."),
    ("Prueba de embarazo (hCG)", "Hormonas", "Negativo: <5 mUI/mL. Positivo: >25 mUI/mL."),
]

EXAMENES_ORINA = [
    # Físicos
    ("Color orina", "Orina · Físicos", "Amarillo claro a ámbar (variable con hidratación)."),
    ("Transparencia orina", "Orina · Físicos", "Transparente. Turbia sugiere cristales, bacterias o leucocitos."),
    ("Densidad orina", "Orina · Físicos", "1.005 - 1.030"),
    ("Olor orina", "Orina · Físicos", "Característico suave. Amoniacal o fétido sugiere infección."),
    # Químicos (tira reactiva)
    ("pH urinario", "Orina · Químicos", "4.5 - 8.0 (promedio ~6.0)"),
    ("Proteínas en orina", "Orina · Químicos", "Negativo a trazas. Positivo sugiere proteinuria."),
    ("Glucosa en orina", "Orina · Químicos", "Negativo. Positivo sugiere glucemia >180 mg/dL."),
    ("Cetonas en orina", "Orina · Químicos", "Negativo. Positivo sugiere cetosis o cetoacidosis."),
    ("Nitritos en orina", "Orina · Químicos", "Negativo. Positivo sugiere bacteriuria por gram negativos."),
    ("Leucocitos (esterasa)", "Orina · Químicos", "Negativo. Positivo sugiere infección urinaria."),
    ("Sangre en orina", "Orina · Químicos", "Negativo. Positivo: hematuria o hemoglobinuria."),
    # Microscópico
    ("Glóbulos rojos en sedimento", "Orina · Microscópico", "0 - 3 por campo. Hematuria: >3/campo."),
    ("Glóbulos blancos en sedimento", "Orina · Microscópico", "0 - 5 por campo. Piuria: >5/campo."),
    ("Bacterias en sedimento", "Orina · Microscópico", "Ausentes o escasas. Abundantes sugieren bacteriuria."),
    ("Cristales en sedimento", "Orina · Microscópico", "Ausentes o escasos (tipo depende del pH)."),
    ("Células epiteliales en sedimento", "Orina · Microscópico", "Escasas. Abundantes sugieren contaminación."),
]


class Command(BaseCommand):
    help = "Siembra solo el catálogo de exámenes y perfiles (sin pacientes/médicos/empleados). Idempotente."

    def handle(self, *args, **options):
        total = self._seed_examenes(EXAMENES)
        total += self._seed_examenes(EXAMENES_ORINA)
        self._seed_perfil_orina()
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Catálogo sembrado: {Examen.objects.count()} exámenes en BD ({total} nuevos/actualizados esta corrida)"
        ))

    def _seed_examenes(self, lista):
        count = 0
        for nombre, perfil, valores_ref in lista:
            examen, creado = Examen.objects.get_or_create(
                nombre_completo=nombre,
                defaults={
                    "perfil": perfil,
                    "valores_ref": valores_ref,
                    "activo": True,
                },
            )
            if creado or not examen.costos.filter(activo=True).exists():
                CostoExamen.objects.filter(examen=examen, activo=True).update(activo=False)
                precio = Decimal(str(random.randint(8, 45)))
                CostoExamen.objects.create(examen=examen, precio=precio, activo=True)
                count += 1
        return count

    def _seed_perfil_orina(self):
        perfil, _ = Perfil.objects.get_or_create(nombre="Examen de Orina (Uroanálisis)")
        perfil.examenes.set(
            Examen.objects.filter(
                Q(perfil__startswith="Orina ·") | Q(nombre_completo="Uroanálisis completo")
            )
        )
        self.stdout.write(f"  Perfil uroanálisis: {perfil.examenes.count()} exámenes")
