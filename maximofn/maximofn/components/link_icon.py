import reflex as rx
from maximofn.styles.sizes import Size as Size

def link_icon(icon: str, href: str, alt: str, icon_width=Size.MEDIUM.value, icon_margin_x=None) -> rx.Component:
    return rx.link(
        rx.image(
            src = icon,
            width = icon_width,
            margin_x = icon_margin_x,
            alt = alt,
        ),
        href = href,
        is_external = True,
    )