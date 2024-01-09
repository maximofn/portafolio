
from maximofn.styles.colors import Color
from maximofn.styles.sizes import Size

DEBUG = False
# DEBUG = True

if DEBUG:
    border = "5px solid yellow"
    border_radius = "15px"
else:
    border = "0px"
    border_radius = "0px"

presentation_style = {
    # "display": "flex",
    # "flex-direction": "row",                     # direction of the main axis
    # "align-items": "center",                    # alignment of items on the cross axis
    "align-content": "space-between",                    # alignment of content on the main axis
    # "align-content": "flex-start",                      # alignment of content on the cross axis
    # "background-color": Color.BACKGROUND.value,
    "width": "100%",
    "color": Color.SECONDARY.value,
    # "margin_top": "256px",
    
    # DEBUG
    "border": border,
    "border-radius": border_radius,

}

presentation_text_style = {
    "display": "flex",
    "flex-direction": "column",                     # direction of the main axis
    "align-items": "flex-start",                    # alignment of items on the cross axis
    # "justify-content": "space-between",                    # alignment of content on the main axis
    "align-content": "flex-start",                      # alignment of content on the cross axis
    
    # DEBUG
    "border": border,
    "border-radius": border_radius,
}

presentation_name_style = {
    "color": Color.BLUE.value,
    "font-size": Size.XXXLARGE.value,
    "font-weight": "bold",
    "margin_bottom": "12px",
    
    # DEBUG
    "border": border,
    "border-radius": border_radius,
}

presentation_position_style = {
    "color": Color.SECONDARY.value,
    "font-size": Size.XXLARGE.value,
    "font-weight": "bold",
    "margin_bottom": "8px",
    
    # # DEBUG
    "border": border,
    "border-radius": border_radius,
}

presentation_resume_style = {
    "display": "flex",
    "flex-direction": "column",

    "color": Color.SECONDARY.value,
    "font-size": Size.XLARGE.value,
    "margin_bottom": "8px",
    "gap": "6px",
    
    # # DEBUG
    "border": border,
    "border-radius": border_radius,
}