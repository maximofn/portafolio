DEBUG = True

if DEBUG:
    gap = "30px"
    border = "5px solid purple"
    border_radius = "15px"
else:
    gap = "0px"
    border = "0px"
    border_radius = "0px"

content_style = {
    "background-color": "black",
    "justify-content": "flex-start",
    "gap": gap,
    "border": border,
    "border-radius": border_radius,
    "align-items": "start",
    "max-width": "1500px",
    # "margin_top": "50px",
}