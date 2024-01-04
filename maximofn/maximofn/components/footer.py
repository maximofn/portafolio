import reflex as rx

def footer() -> rx.Component:
    return rx.hstack(
        rx.text(
            "Política de privacidad",
        ),
        rx.text(
            "Política de cookies",
        ),
        rx.text(
            "Aviso legal",
        ),
        rx.text(
            "Contacto",
        ),
        width = "100%",
        background_color = "blue",
        # position = "sticky",
        z_index = 0,
        bottom = 0,
    )