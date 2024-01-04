import reflex as rx

def custom_work_experience(company: str, position: str, date_start: str, date_end: str, responsabilities: list, key_accomplishments: list) -> rx.Component:
    if responsabilities is not None and key_accomplishments is not None:
        return rx.vstack(
                rx.text(f"{position} en {company}"),
                rx.text(f"{date_start}  - {date_end}"),
                rx.text("Responsabilidades:"),
                rx.unordered_list(items=responsabilities),
                rx.text("Logros:"),
                rx.unordered_list(items=key_accomplishments),
        )
    elif responsabilities is not None and key_accomplishments is None:
        return rx.vstack(
                rx.text(f"{position} en {company}"),
                rx.text(f"{date_start} - {date_end}"),
                rx.text("Responsabilidades:"),
                rx.unordered_list(items=responsabilities),
        )
    elif responsabilities is None and key_accomplishments is not None:
        return rx.vstack(
                rx.text(f"{position} en {company}"),
                rx.text(f"{date_start} - {date_end}"),
                rx.text("Logros:"),
                rx.unordered_list(items=key_accomplishments),
        )
    else:
        return rx.vstack(
                rx.text(f"{position} en {company}"),
                rx.text(f"{date_start} - {date_end}"),
        )