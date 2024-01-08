import reflex as rx
from maximofn.styles.work_experience_styles import work_experience_time_line_style

def time_line(num_rows: int) -> rx.Component:
    work_experience_time_line_style["grid_row_end"] = num_rows + 2,
    return rx.box(
        style = work_experience_time_line_style,
    )