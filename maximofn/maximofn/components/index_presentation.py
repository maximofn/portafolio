import reflex as rx

def index_presentation() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading(
                    "MaximoFN",
                ),
                rx.box(
                    rx.span(
                        "Machine Learning"
                    ),
                    " Engineer",
                ),
            ),
            rx.image(
                src = "maximo-0014.webp",
                width = "200px",
            ),
        ),
    )