from maximofn.styles.fonts import Font, FontWeight
from maximofn.styles.colors import Color

# Style sheets
STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;500&display=swap",
    "https://fonts.googleapis.com/css2?family=Comfortaa:wght@500&display=swap",
]

DEBUG = False
# DEBUG = True

if DEBUG:
    border = "5px solid purple"
else:
    border = "0px"

page_style = {
    "display": "flex",
    "flex-direction": "column",                     # direction of the main axis
    "align-items": "center",                    # alignment of items on the cross axis
    "justify-content": "center",                    # alignment of content on the main axis
    "align-content": "center",                      # alignment of content on the cross axis
    "background-color": Color.BACKGROUND.value,
    "font_family": Font.DEFAULT.value,
    "font_weight": FontWeight.LIGHT.value,

    # DEBUG
    "border": border,
}