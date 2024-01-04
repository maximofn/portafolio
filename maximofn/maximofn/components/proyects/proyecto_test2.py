import reflex as rx

def proyecto_test2() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Proyecto de prueba 2",
        ),
    )