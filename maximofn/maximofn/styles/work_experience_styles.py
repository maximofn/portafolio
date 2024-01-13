from maximofn.styles.colors import Color
from maximofn.styles.sizes import Size

DEBUG = False
# DEBUG = True

TIME_LINE_WIDTH = "5px"
TIME_LINE_LINEWIDTH = "3px"

if DEBUG:
    border = "5px solid yellow"
    border_radius = "15px"
else:
    border = "0px"
    border_radius = "0px"

work_experience_style = {
    "display": "flex",
    "flex-direction": "column",                     # direction of the main axis
    "align-items": "stretch",                    # alignment of items on the cross axis
    "justify-content": "flex-start",                    # alignment of content on the main axis
    "align-content": "flex-start",                  # alignment of content on the cross axis
    "gap": "12px",

    # DEBUG
    "border": border,
    "border-radius": border_radius,
}

work_experience_title_style = {
    "color": Color.BLUE.value,
    "font-size": Size.XXXLARGE.value,
    "font-weight": "bold",

    # DEBUG
    "border": border,
}

work_experience_stack_style_desktop = {
    "display": "grid",
    "align-content": "start",   # Top align vertically
    "align-items": "start",    # Center vertically
    "justify-content": "start",   # Left align horizontally
    "justify-items": "stretch",   # Left align horizontally
    "grid-template-columns": f"auto {TIME_LINE_WIDTH} auto",
    "gap": "12px",

    # DEBUG
    "border": border,
}

work_experience_stack_style_mobile_and_tablet = {
    "display": "flex",
    "flex-direction": "column",                     # direction of the main axis
    "align-items": "stretch",                    # alignment of items on the cross axis
    "justify-content": "flex-start",                    # alignment of content on the main axis
    "align-content": "flex-start",                  # alignment of content on the cross axis
    "gap": "12px",

    # DEBUG
    "border": border,
}

work_experience_time_line_style = {
    "grid_row_start": "1",
    "grid_row_end": "",
    "grid_column_start": "2",

    "border": f"{TIME_LINE_LINEWIDTH} solid {Color.WHITE.value}",
    "border-radius": "15px",
    "align-self": "stretch",
}

custom_work_experience_style = {
    "display": "flex",
    "flex-direction": "column",                     # direction of the main axis
    "align-items": "stretch",                    # alignment of items on the cross axis
    "justify-content": "flex-start",                    # alignment of content on the main axis
    "align-content": "stretch",                  # alignment of content on the cross axis

    "gap": "6px",
    "background-color": Color.GRAY.value,
    "border-radius": "15px",
    "border-bottom": f"2px solid {Color.WHITE.value}",
    "border-right": f"2px solid {Color.WHITE.value}",

    "padding": "12px",
}

custom_work_experience_date_style = {
    "align-self": "flex-end",
    "color": Color.WHITE.value,
    "font-size": Size.LARGE.value,
    "font-weight": "bold",
}

custom_work_experience_title_style = {
    "color": Color.WHITE.value,
    "font-size": Size.XXLARGE.value,
    "font-weight": "bold",
}

custom_work_experience_subtitle_style = {
    "color": Color.WHITE.value,
    "font-size": Size.XLARGE.value,
    "font-weight": "bold",
}

custom_work_experience_list_style = {
    "color": Color.SECONDARY.value,
    "font-size": Size.LARGE.value,
    # "font-weight": "bold",
    # "list-style-type": "none",
    "padding-left": "24px",
}