from rxconfig import config
import reflex as rx
from maximofn.components.header import header
from maximofn.components.footer import footer
from maximofn.components.index_presentation import index_presentation
from maximofn.components.work_experience.work_experience import work_experience

class State(rx.State):
    """The app state."""

    pass


def index() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(
                header(),
                index_presentation(),
                work_experience(),
                width = "100%",
            ),
        ),
        footer(),
    )


# Add state and page to the app.
app = rx.App()
app.add_page(index)
app.compile()
