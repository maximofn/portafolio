import reflex as rx

def header() -> rx.Component:
    return rx.flex(
        rx.span(
            "Maximo",
            color = "white",
        ),
        rx.span(
            "FN",
            color = "gray",
        ),
        rx.spacer(),
        rx.image(
            src="favicon.ico",
        ),
        width = "100%",
        background_color = "blue",
        position = "sticky",
        z_index = 999,
        top = 0,
    )