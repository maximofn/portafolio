import reflex as rx

from maximofn.styles.colors import Color
from maximofn.styles.sizes import Size
from maximofn.styles.presentation_style import presentation_style_desktop, presentation_style_mobile_tablet, presentation_text_style, presentation_name_style, presentation_position_style, presentation_resume_style

import time

YEAR_START = 2019

def photo() -> rx.Component:
    src = "maximo-0014.webp"
    border_radius = "5%"

    photo_box = rx.box(
        rx.mobile_and_tablet(
            rx.center(
                rx.image(
                    src = src,
                    width = "200px",
                    border_radius = border_radius,
                    justify_content = "center",
                )
            )
        ),
        rx.desktop_only(
            rx.image(
                src = src,
                width = "300px",
                border_radius = border_radius,
            ),
        ),
    )
    return photo_box

def presentation_name() -> rx.Component:
    return rx.heading(
        "MaximoFN",
        style=presentation_name_style,
    )

def presentation_position() -> rx.Component:
    return rx.flex(
        rx.box(
            rx.span(
                "Machine Learning ", 
                color=Color.ORANGE.value,
            ),
            "Engineer. Visión por computador y LLMs.",
            style=presentation_position_style,
        ),
    )

def presentation_resume() -> rx.Component:
    return rx.flex(
        rx.text(
            f"+{time.localtime().tm_year - YEAR_START} años de experiencia en inteligencia artificial.",
        ),
        rx.box(
            "Optimización de modelos con ",
            rx.span(
                "TensorRT", 
                color=Color.GREEN.value,
            ),
            ". Experiencia en dispositivos ",
            rx.span(
                "Jetson", 
                color=Color.GREEN.value,
            ),
        ),
        style=presentation_resume_style,
    )

def presentation_text() -> rx.Component:
    presentation_text = rx.vstack(
        presentation_name(),
        presentation_position(),
        presentation_resume(),
        style = presentation_text_style,
    )
    return presentation_text

def presentation() -> rx.Component:

    presentation = rx.box(
        rx.desktop_only(
            rx.box(
                presentation_text(),
                photo(),
                style=presentation_style_desktop,
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                photo(),
                presentation_text(),
                style=presentation_style_mobile_tablet,
            ),
        )
    )

    return presentation