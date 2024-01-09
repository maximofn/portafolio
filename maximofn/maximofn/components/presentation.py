import reflex as rx

from maximofn.styles.colors import Color
from maximofn.styles.sizes import Size
from maximofn.styles.presentation_style import presentation_style, presentation_name_style, presentation_position_style

import time

YEAR_START = 2019

def photo() -> rx.Component:
    return rx.image(
        src = "maximo-0014.webp",
        width = "200px",
    )

def presentation_name() -> rx.Component:
    return rx.heading(
        "MaximoFN",
        style=presentation_name_style,
    )

def presentation_position() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Machine Learning",
            color = Color.ORANGE.value,
        ),
        rx.text(
            " Engineer. Visión por computador y LLMs................",
        ),
        # style=presentation_position_style,
    )

def presentation_text() -> rx.Component:
    presentation_text = rx.vstack(
        presentation_name(),
        presentation_position(),
        rx.flex(
            rx.box(
                rx.span(
                    "Machine Learning",
                    color = Color.ORANGE.value,
                ),
                " Engineer. Visión por computador y LLMs",
                font_size = Size.XXLARGE.value,
                margin_bottom = "12px",
            ),
            border_color = Color.BLUE.value,
            border_width = "2px",
            margin= "0px",
        ),
        rx.flex(
            rx.text(
                f"+{time.localtime().tm_year - YEAR_START} años de experiencia en inteligencia artificial.",
                font_size = Size.MEDIUM.value,
                margin_bottom = "6px",
            ),
        ),
        rx.flex(
            "Optimización de modelos con ",
            rx.span(
                " TensorRT",
                color = Color.GREEN.value,
            ),
            ". Experiencia en dispositivos ",
            rx.span(
                " Jetson",
                color = Color.GREEN.value,
            ),
            ".",
            font_size = Size.MEDIUM.value,
            border_color = Color.ORANGE.value,
            border_width = "2px",
            margin = "0px"
        ),
        align_items="flex-start",
        border_color = Color.BLUE.value,
        border_width = "2px",
    )

    return presentation_text

def presentation() -> rx.Component:
    presentation = rx.box(
        presentation_text(),
        photo(),
        style=presentation_style,
    )

    return presentation