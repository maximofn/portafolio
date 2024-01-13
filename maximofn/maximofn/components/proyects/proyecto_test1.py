import reflex as rx

from maximofn.styles.colors import Color

def proyecto_test1() -> rx.Component:
    return rx.vstack(
        rx.link(
            "Proyecto de prueba 1",
            href="/proyecto_test1",
            color=Color.GREEN.value,
        ),
    )