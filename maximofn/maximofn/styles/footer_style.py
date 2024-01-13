from maximofn.styles.colors import Color
from maximofn.styles.sizes import Size

DEBUG = False
# DEBUG = True

if DEBUG:
    border = "5px solid blue"
    border_radius = "15px"
else:
    border = "0px"
    border_radius = "0px"

footer_style = {
    "display": "flex",
    "flex-direction": "row",                     # direction of the main axis
    "align-items": "stretch",                    # alignment of items on the cross axis
    "justify-content": "stretch",                    # alignment of content on the main axis
    "align-content": "flex-start",                  # alignment of content on the cross axis
    "gap": "12px",
    "width": "100%",
    "background-color": Color.BACKGROUND.value,
    "padding": "10px 20px 10px 20px",
    "margin-top": Size.XXXLARGE.value,
    "height": "auto",
    "align": "center",

    # DEBUG
    "border": border,
    "border-radius": border_radius,
}