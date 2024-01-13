import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def indra_trainee(row_start: int, row_end: int, column: int) -> rx.Component:
    return custom_work_experience(
        company = "Indra",
        position = "Becario",
        date_start = "Enero 2013",
        date_end = "Mayo 2014",
        responsabilities = [
            "Desarrollo hardware",
            "Test de hardware",
            "Documentación",
            "Ayuda en la gestión de proyectos",
        ],
        key_accomplishments = None,
        row_start=row_start,
        row_end=row_end,
        column=column,
    )