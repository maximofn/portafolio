import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def indra_trainee() -> rx.Component:
    return custom_work_experience(
        company = "Indra",
        position = "Becario",
        date_start = "Enero 2013",
        date_end = "Mayo 2014",
        responsabilities = [
            "Desarrollo hardware y software",
        ],
        key_accomplishments = None,
    )