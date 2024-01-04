import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def indra() -> rx.Component:
    return custom_work_experience(
        company = "Indra",
        position = "Ingeniero electrónico",
        date_start = "Mayo 2014",
        date_end = "Octubre 2017",
        responsabilities = [
            "Desarrollo hardware y software",
        ],
        key_accomplishments = None,
    )