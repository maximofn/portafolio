import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def indra(row_start: int, row_end: int, column: int) -> rx.Component:
    return custom_work_experience(
        company = "Indra",
        position = "Ingeniero electrónico",
        date_start = "Mayo 2014",
        date_end = "Octubre 2017",
        responsabilities = [
            "Desarrollo hardware y software",
        ],
        key_accomplishments = None,
        row_start=row_start,
        row_end=row_end,
        column=column,
    )