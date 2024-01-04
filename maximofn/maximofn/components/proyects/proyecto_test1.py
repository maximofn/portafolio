import reflex as rx

def proyecto_test1() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Proyecto de prueba 1",
        ),
    )