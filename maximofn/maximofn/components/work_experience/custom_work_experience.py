import reflex as rx
from maximofn.styles.work_experience_styles import custom_work_experience_style, custom_work_experience_date_style, custom_work_experience_title_style, custom_work_experience_subtitle_style, custom_work_experience_list_style

def custom_work_experience(company: str, position: str, date_start: str, date_end: str, responsabilities: list, key_accomplishments: list, row_start=None, row_end=None, column=None) -> rx.Component:
    if row_start is not None and row_end is not None and column is not None:
        custom_work_experience_style["grid_row_start"] = row_start
        custom_work_experience_style["grid_row_end"] = row_end
        custom_work_experience_style["grid_column_start"] = column
        print(f"row_start: {row_start}, row_end: {row_end}, column: {column}")
    if responsabilities is not None and key_accomplishments is not None:
        return rx.vstack(
                rx.text(f"{position} en {company}", style=custom_work_experience_title_style),
                rx.text("Responsabilidades:", style=custom_work_experience_subtitle_style),
                rx.unordered_list(items=responsabilities, style=custom_work_experience_list_style),
                rx.text("Logros:", style=custom_work_experience_subtitle_style),
                rx.unordered_list(items=key_accomplishments, style=custom_work_experience_list_style),
                rx.text(f"{date_start}  - {date_end}", style=custom_work_experience_date_style),
                style=custom_work_experience_style,
        )
    elif responsabilities is not None and key_accomplishments is None:
        return rx.vstack(
                rx.text(f"{position} en {company}", style=custom_work_experience_title_style),
                rx.text("Responsabilidades:", style=custom_work_experience_subtitle_style),
                rx.unordered_list(items=responsabilities, style=custom_work_experience_list_style),
                rx.text(f"{date_start} - {date_end}", style=custom_work_experience_date_style),
                style=custom_work_experience_style,
        )
    elif responsabilities is None and key_accomplishments is not None:
        return rx.vstack(
                rx.text(f"{position} en {company}", style=custom_work_experience_title_style),
                rx.text("Logros:", style=custom_work_experience_subtitle_style),
                rx.unordered_list(items=key_accomplishments, style=custom_work_experience_list_style),
                rx.text(f"{date_start} - {date_end}", style=custom_work_experience_date_style),
                style=custom_work_experience_style,
        )
    else:
        return rx.vstack(
                rx.text(f"{position} en {company}"),
                rx.text(f"{date_start} - {date_end}"),
                style=custom_work_experience_style,
        )