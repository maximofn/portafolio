import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def arquimea_electronic(row_start: int, row_end: int, column: int) -> rx.Component:
    return custom_work_experience(
        company = "Arqimea",
        position = "Ingeniero electrónico",
        date_start = "Octubre 2017",
        date_end = "Agosto 2019",
        responsabilities = [
            "HW y FW: Diseño y desarrollo de nuevas tecnologías ampliamente utilizadas por otros equipos internos y externos.",
            "Evolución de la arquitectura para responder a futuras necesidades.",
            "Apoyar proactivamente a otros miembros del equipo y ayudarles a alcanzar el éxito.",
            "Cuestionar los procesos del equipo, buscando formas de mejorarlos.",
        ],
        key_accomplishments = [
            "Antes de mi llegada había un diseño de HW diferente para cada UAV y para cada estación terrestre. Unifiqué los diseños en uno solo. Esto significaba que el 80%\ del desarrollo de FW de un UAV era heredado por el otro UAV, ahorrando así meses de desarrollo. También eliminó los diseños duplicados que hacían lo mismo."
        ],
        row_start=row_start,
        row_end=row_end,
        column=column,
    )