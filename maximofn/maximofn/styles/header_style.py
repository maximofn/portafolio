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

header_style = {
    "display": "flex",
    "flex-direction": "row",                     # direction of the main axis
    "align-items": "stretch",                    # alignment of items on the cross axis
    "justify-content": "stretch",                    # alignment of content on the main axis
    "align-content": "flex-start",                  # alignment of content on the cross axis
    "gap": "12px",
    "width": "100%",
    "background-color": Color.BACKGROUND.value,
    "padding": "10px 20px 10px 20px",
    "height": "auto",
    "position": "sticky",
    "top": "0px",
    "left": "0px",
    "align": "center",
    "opacity": "0.9",
    "border-bottom": f"1px solid {Color.WHITE.value}",

    # DEBUG
    # "border": border,
    # "border-radius": border_radius,
}

header_languajes_style = {
    "margin-right": Size.XLARGE.value,
    "align-items": "center",

    # DEBUG
    "border": border,
    "border-radius": border_radius,
}

header_one_languaje_style = {
    "padding": "0px",
    "border": "none",
    "background-color": "transparent",
    "_hover": {
        "cursor": "pointer",
    },

    # DEBUG
    "border": border,
    "border-radius": border_radius,
}