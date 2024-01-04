import reflex as rx
from maximofn.components.work_experience.indra_trainee import indra_trainee
from maximofn.components.work_experience.indra import indra
from maximofn.components.work_experience.arquimea_electronic import arquimea_electronic
from maximofn.components.work_experience.arquimea_deep_learning import arquimea_deep_learning
from maximofn.components.work_experience.sener import sener

def work_experience() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Experiencia laboral",
        ),
        sener(),
        arquimea_deep_learning(),
        arquimea_electronic(),
        indra(),
        indra_trainee(),
    )