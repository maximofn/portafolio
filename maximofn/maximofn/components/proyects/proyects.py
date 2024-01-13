import reflex as rx
from maximofn.components.proyects.proyecto_test1 import proyecto_test1
from maximofn.components.proyects.proyecto_test2 import proyecto_test2
from maximofn.components.proyects.proyecto_test3 import proyecto_test3

from maximofn.styles.work_experience_styles import work_experience_title_style, work_experience_style

def link_to_proyect(thumnail: str, alt: str, link: str) -> rx.Component:
    return rx.link(
        rx.image(
            src=thumnail,
            alt=alt,
            style={
                "width": "100px",
            },
        ),
        href=link,
    )

def proyects() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Proyectos",
            style = work_experience_title_style,
        ),
        link_to_proyect(thumnail="maximo-0014.webp", alt="Link to proyect", link="/proyecto_test1"),
        proyecto_test1(),
        proyecto_test2(),
        proyecto_test3(),
        style = work_experience_style,
    )