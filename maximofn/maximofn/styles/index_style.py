from maximofn.styles.colors import Color

DEBUG = False
# DEBUG = True

if DEBUG:
    border = "5px solid purple"
    border_radius = "15px"
else:
    border = "0px"
    border_radius = "0px"

content_style = {
    "display": "flex",
    "flex-direction": "column",                     # direction of the main axis
    "align-items": "stretch",                    # alignment of items on the cross axis
    "justify-content": "flex-start",                    # alignment of content on the main axis
    "align-content": "flex-start",                      # alignment of content on the cross axis
    "max_width": "1500px",
    "background-color": Color.BACKGROUND.value,
    "gap": "100px",
    "margin": "0px 12px",

    # DEBUG
    "border": border,
    "border-radius": border_radius,
}