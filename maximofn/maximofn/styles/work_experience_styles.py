DEBUG = True

if DEBUG:
    gap = "30px"
    border = "5px solid purple"
    border_section = "5px solid yellow"
    border_radius = "15px"
    background_color_title = "green"
    background_color_stack = "red"
else:
    gap = "0px"
    border = "0px"
    border_section = "0px"
    border_radius = "0px"
    background_color_title = ""
    background_color_stack = ""

work_experience_style = {
    "gap": gap,
    "border": border,
    "border-radius": border_radius,
    "align-items": "flex-start",
}

work_experience_title_style = {
    "font-size": "40px",
    "font-weight": "bold",
    border: border_section,
    "background-color": background_color_title,
}

time_line_width = "3px"

work_experience_stack_style = {
    "display": "grid",
    "align-items": "center",    # Center vertically
    "justify-items": "start",   # Left align horizontally
    "grid-template-columns": f"auto {time_line_width} auto",
    # DEBUG
    "background-color": background_color_stack,
    # "gap": gap,
    # "border": border_section,
}

work_experience_time_line_style = {
    "grid_row_start": "1",
    "grid_row_end": "",
    "grid_column_start": "2",
    "background-color": "lightgray",
    "border": f"{time_line_width} solid black",
    "border-radius": "15px",
    "align-self": "stretch",
}

custom_work_experience_style = {
    "display": "block",
    "background-color": "lightgray",
    "border-radius": "15px",
    "width": "600px",
    "color": "gray",
    "padding": "10px 10px 10px 30px",
}

custom_work_experience_date_style = {
    "float": "right",
    "color": "white",
}

custom_work_experience_title_style = {
    "color": "white",
    "font-size": "20px",
    "font-weight": "bold",
}

custom_work_experience_subtitle_style = {
    "color": "white",
    "font-size": "15px",
    "font-weight": "bold",
}

custom_work_experience_list_style = {
    # "color": "white",
    # "font-size": "10px",
    # "font-weight": "bold",
    # "list-style-type": "none",
}