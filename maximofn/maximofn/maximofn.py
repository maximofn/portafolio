from rxconfig import config
import reflex as rx
from maximofn.components.header import header
from maximofn.components.footer import footer
from maximofn.components.presentation import presentation
from maximofn.components.work_experience.work_experience import work_experience
from maximofn.components.proyects.proyects import proyects
from maximofn.components.blog.all_posts import all_posts
from maximofn.styles.index_style import content_style
from maximofn.styles.page_style import page_style, STYLESHEETS

class State(rx.State):
    """The app state."""

    pass


def index() -> rx.Component:
    return rx.box(
        header(),
        rx.box(
            presentation(),
            work_experience(),
            proyects(),
            all_posts(),
            style = content_style,
        ),
        footer(),
        style=page_style,
    )


# Add state and page to the app.
app = rx.App(
    stylesheets=STYLESHEETS,
)
app.add_page(index)
app.compile()
