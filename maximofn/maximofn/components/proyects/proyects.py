import reflex as rx
from maximofn.components.proyects.proyecto_test1 import proyecto_test1
from maximofn.components.proyects.proyecto_test2 import proyecto_test2
from maximofn.components.proyects.proyecto_test3 import proyecto_test3

def proyects() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Proyectos",
        ),
        proyecto_test1(),
        proyecto_test2(),
        proyecto_test3(),
    )