import reflex as rx

from maximofn.styles.footer_style import footer_style
from maximofn.styles.colors import Color

def footer() -> rx.Component:
    return rx.hstack(
        rx.text(
            "Política de privacidad",
            color = Color.SECONDARY.value,
        ),
        rx.text(
            "Política de cookies",
            color = Color.SECONDARY.value,
        ),
        rx.text(
            "Aviso legal",
            color = Color.SECONDARY.value,
        ),
        rx.text(
            "Contacto",
            color = Color.SECONDARY.value,
        ),
        style=footer_style,
    )