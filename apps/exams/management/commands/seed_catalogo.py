from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.exams.models import CostoExamen, Examen

# Precios de referencia por perfil (ajústalos a tu mercado)
PRECIO_PERFIL = {
    "Hematología": 12, "Coagulación": 18, "Química Sanguínea": 10,
    "Perfil Lipídico": 12, "Hepáticas": 12, "Renal": 15,
    "Electrolitos": 10, "Uroanálisis": 12, "Tiroides": 25,
    "Hormonas": 25, "Marcadores Tumorales": 30, "Serología / Infecciosas": 15,
    "Vitaminas y Minerales": 20, "Marcadores Cardíacos": 25,
    "Páncreas": 12, "Heces": 10, "Inmunología": 25, "Otros": 15,
}

CATALOGO = {
    "Hematología": [
        ("Hematología completa (Hemograma)", "Leucocitos 4.500-11.000/mm³; Hemoglobina 12-17 g/dL; Plaquetas 150.000-450.000/mm³"),
        ("Hemoglobina", "12-17 g/dL"),
        ("Hematocrito", "36-53%"),
        ("Recuento de glóbulos rojos", "4.2-5.9 M/mm³"),
        ("Leucocitos", "4.500-11.000/mm³"),
        ("Plaquetas", "150.000-450.000/mm³"),
        ("Reticulocitos", "0.5-2.5%"),
        ("Velocidad de sedimentación (VSG)", "0-20 mm/h"),
        ("Frotis de sangre periférica", "Sin alteraciones"),
        ("Grupo sanguíneo ABO", "Tipificación"),
        ("Factor Rh", "Positivo / Negativo"),
        ("Recuento de eosinófilos", "0-500/mm³"),
    ],
    "Coagulación": [
        ("Tiempo de Protrombina (TP)", "11-13.5 segundos"),
        ("INR", "0.8-1.2"),
        ("Tiempo de Tromboplastina Parcial (TTP)", "25-35 segundos"),
        ("Fibrinógeno", "200-400 mg/dL"),
        ("Dímero D", "<0.5 µg/mL"),
        ("Tiempo de sangría", "1-9 minutos"),
        ("Tiempo de coagulación", "5-11 minutos"),
    ],
    "Química Sanguínea": [
        ("Glucosa en ayunas", "70-100 mg/dL"),
        ("Glucosa postprandial", "<140 mg/dL"),
        ("Hemoglobina glicosilada (HbA1c)", "4.0-5.7%"),
        ("Urea", "15-45 mg/dL"),
        ("Creatinina", "0.6-1.3 mg/dL"),
        ("Ácido úrico", "2.4-7.0 mg/dL"),
        ("Proteínas totales", "6.0-8.3 g/dL"),
        ("Albúmina", "3.5-5.5 g/dL"),
        ("Calcio", "8.5-10.5 mg/dL"),
        ("Fósforo", "2.5-4.5 mg/dL"),
        ("Magnesio", "1.7-2.2 mg/dL"),
    ],
    "Perfil Lipídico": [
        ("Colesterol total", "<200 mg/dL"),
        ("HDL", ">40 mg/dL (H) / >50 mg/dL (M)"),
        ("LDL", "<100 mg/dL"),
        ("VLDL", "5-40 mg/dL"),
        ("Triglicéridos", "<150 mg/dL"),
        ("Índice aterogénico", "<5"),
    ],
    "Hepáticas": [
        ("Bilirrubina total", "0.1-1.2 mg/dL"),
        ("Bilirrubina directa", "0.0-0.3 mg/dL"),
        ("Bilirrubina indirecta", "0.1-0.9 mg/dL"),
        ("TGO (AST)", "5-40 U/L"),
        ("TGP (ALT)", "7-56 U/L"),
        ("Fosfatasa alcalina", "44-147 U/L"),
        ("GGT", "7-50 U/L"),
        ("LDH", "140-280 U/L"),
    ],
    "Renal": [
        ("Depuración de creatinina", "90-120 mL/min"),
        ("Microalbuminuria", "<30 mg/24h"),
        ("Cistatina C", "0.5-1.0 mg/L"),
    ],
    "Electrolitos": [
        ("Sodio", "135-145 mEq/L"),
        ("Potasio", "3.5-5.0 mEq/L"),
        ("Cloro", "98-107 mEq/L"),
        ("Anión gap", "8-16 mEq/L"),
    ],
    "Uroanálisis": [
        ("Uroanálisis completo", "pH 4.5-8.0; densidad 1.005-1.030; sin proteínas ni glucosa"),
        ("Urocultivo con antibiograma", "Sin desarrollo bacteriano"),
        ("Proteínas en orina de 24 horas", "<150 mg/24h"),
        ("Prueba de embarazo en orina", "Negativo"),
    ],
    "Tiroides": [
        ("TSH", "0.4-4.0 µUI/mL"),
        ("T4 libre", "0.8-1.8 ng/dL"),
        ("T3 total", "80-200 ng/dL"),
        ("T3 libre", "2.3-4.2 pg/mL"),
        ("Anticuerpos anti-TPO", "<35 UI/mL"),
        ("Anticuerpos antitiroglobulina", "<40 UI/mL"),
    ],
    "Hormonas": [
        ("Prolactina", "2-25 ng/mL"),
        ("FSH", "Variable según sexo y ciclo"),
        ("LH", "Variable según sexo y ciclo"),
        ("Estradiol", "Variable según sexo y ciclo"),
        ("Progesterona", "Variable según fase del ciclo"),
        ("Testosterona total", "240-950 ng/dL (H)"),
        ("Cortisol (8 am)", "5-23 µg/dL"),
        ("Insulina", "2-25 µUI/mL"),
        ("Péptido C", "1.1-4.4 ng/mL"),
        ("Hormona antimülleriana (AMH)", "Variable según edad y sexo"),
    ],
    "Marcadores Tumorales": [
        ("PSA (antígeno prostático)", "<4 ng/mL"),
        ("Alfa-fetoproteína", "<10 ng/mL"),
        ("CEA", "<5 ng/mL"),
        ("CA-125", "<35 U/mL"),
        ("CA 15-3", "<30 U/mL"),
        ("CA 19-9", "<37 U/mL"),
        ("Beta-hCG cuantitativa", "<5 mUI/mL (no embarazada)"),
    ],
    "Serología / Infecciosas": [
        ("HIV (ELISA)", "No reactivo"),
        ("HIV (prueba rápida)", "No reactivo"),
        ("Hepatitis B (HBsAg)", "No reactivo"),
        ("Anticuerpos anti-HBs", ">10 mUI/mL (inmune)"),
        ("Hepatitis C (anti-HCV)", "No reactivo"),
        ("VDRL", "No reactivo"),
        ("RPR", "No reactivo"),
        ("ASO", "<200 UI/mL"),
        ("Proteína C reactiva (PCR)", "<5 mg/L"),
        ("Factor reumatoide", "<14 UI/mL"),
        ("Widal", "<1:80"),
        ("Dengue (NS1)", "No reactivo"),
        ("Dengue (IgG/IgM)", "No reactivo"),
        ("Toxoplasma (IgG)", "Variable"),
        ("Toxoplasma (IgM)", "No reactivo"),
        ("Rubéola (IgG)", "Variable (inmunidad)"),
        ("Rubéola (IgM)", "No reactivo"),
        ("Helicobacter pylori (antígeno en heces)", "Negativo"),
    ],
    "Vitaminas y Minerales": [
        ("Vitamina D (25-OH)", "20-50 ng/mL"),
        ("Vitamina B12", "200-900 pg/mL"),
        ("Ácido fólico", "3-17 ng/mL"),
        ("Hierro sérico", "60-170 µg/dL"),
        ("Ferritina", "20-250 ng/mL"),
        ("TIBC (capacidad fijación de hierro)", "250-370 µg/dL"),
    ],
    "Marcadores Cardíacos": [
        ("Troponina I", "<0.04 ng/mL"),
        ("CK-MB", "<5 ng/mL"),
        ("CPK total", "39-308 U/L"),
        ("NT-proBNP", "<125 pg/mL"),
        ("Homocisteína", "5-15 µmol/L"),
    ],
    "Páncreas": [
        ("Amilasa", "25-125 U/L"),
        ("Lipasa", "10-140 U/L"),
    ],
    "Heces": [
        ("Coproanálisis", "Sin alteraciones"),
        ("Sangre oculta en heces", "Negativo"),
        ("Parásitos en heces", "Negativo"),
        ("Coprocultivo", "Sin desarrollo de patógenos"),
    ],
    "Inmunología": [
        ("ANA (anticuerpos antinucleares)", "<1:40"),
        ("Anti-DNA", "<10 UI/mL"),
        ("Complemento C3", "90-180 mg/dL"),
        ("Complemento C4", "10-40 mg/dL"),
        ("IgE total", "<100 UI/mL"),
        ("IgG", "700-1600 mg/dL"),
        ("IgA", "70-400 mg/dL"),
        ("IgM", "40-230 mg/dL"),
    ],
    "Otros": [
        ("Alcohol en sangre", "<0.0 g/dL"),
        ("Colinesterasa", "5.3-12.9 U/L"),
        ("Ceruloplasmina", "20-60 mg/dL"),
        ("Amonio", "15-45 µg/dL"),
        ("Ácido láctico", "0.5-2.2 mmol/L"),
    ],
}


class Command(BaseCommand):
    help = "Carga el catálogo completo de exámenes de laboratorio por perfil"

    @transaction.atomic
    def handle(self, *args, **options):
        nuevos = 0
        for perfil, examenes in CATALOGO.items():
            precio = Decimal(str(PRECIO_PERFIL.get(perfil, 15)))

            for nombre, valores_ref in examenes:
                examen, creado = Examen.objects.get_or_create(
                    nombre_completo=nombre,
                    defaults={
                        "perfil": perfil,
                        "valores_ref": valores_ref,
                        "activo": True,
                    },
                )

                if creado:
                    CostoExamen.objects.create(
                        examen=examen, precio=precio, activo=True
                    )
                    nuevos += 1
                elif not examen.costos.filter(activo=True).exists():
                    CostoExamen.objects.create(
                        examen=examen, precio=precio, activo=True
                    )

        total = Examen.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"✓ {nuevos} exámenes nuevos. Catálogo total: {total} exámenes"
        ))
