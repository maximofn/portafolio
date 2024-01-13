import reflex as rx
from maximofn.styles.colors import Color
from maximofn.styles.fonts import Font
from maximofn.styles.sizes import Size as Size

def logo_long() -> rx.Component:
    return rx.flex(
        rx.span(
            "Maximo",
            color = Color.BLUE.value,
        ),
        rx.span(
            "FN",
            color = Color.WHITE.value,
        ),
        align="center",
        font_family = Font.LOGO.value,
        font_size = Size.MEDIUM.value,
        font_weight = "bold",
    )

def logo_short() -> rx.Component:
    return rx.flex(
        rx.span(
            "M",
            color = Color.BLUE.value,
        ),
        rx.span(
            "FN",
            color = Color.PRIMARY.value,
        ),
        align="center",
        font_family = Font.LOGO.value,
        font_weight = FontWeight.MEDIUM.value,
        
    )