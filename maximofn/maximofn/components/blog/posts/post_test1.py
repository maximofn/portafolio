import reflex as rx

def post_test1() -> rx.Component:
    return rx.box(
        rx.center(
            rx.text(
                "Proyecto 1",
            ),
        ),
        width = "100%",
    )