import reflex as rx
from maximofn.components.work_experience.indra_trainee import indra_trainee
from maximofn.components.work_experience.indra import indra
from maximofn.components.work_experience.arquimea_electronic import arquimea_electronic
from maximofn.components.work_experience.arquimea_deep_learning import arquimea_deep_learning
from maximofn.components.work_experience.sener import sener
from maximofn.components.work_experience.time_line import time_line
from maximofn.styles.work_experience_styles import work_experience_title_style, work_experience_style, work_experience_stack_style

def work_experience() -> rx.Component:
    column_left = 1
    column_right = 3

    row_start_sener = 1
    row_start_arquimea_deep_learning = row_start_sener + 1
    row_start_arquimea_electronic = row_start_arquimea_deep_learning + 1
    row_start_indra = row_start_arquimea_electronic + 2
    row_start_indra_trainee = row_start_indra + 1

    num_rows = row_start_indra_trainee

    return rx.vstack(
        rx.text(
            "Experiencia laboral",
            style = work_experience_title_style,
        ),
        rx.vstack(
            sener(
                row_start=row_start_sener, 
                row_end=row_start_sener+2, 
                column=column_left
            ),
            arquimea_deep_learning(
                row_start=row_start_arquimea_deep_learning, 
                row_end=row_start_arquimea_deep_learning+2, 
                column=column_right
            ),
            arquimea_electronic(
                row_start=row_start_arquimea_electronic, 
                row_end=row_start_arquimea_electronic+2, 
                column=column_left
            ),
            indra(
                row_start=row_start_indra,
                row_end=row_start_indra+2,
                column=column_right
            ),
            indra_trainee(
                row_start=row_start_indra_trainee,
                row_end=row_start_indra_trainee+2,
                column=column_left
            ),
            time_line(
                num_rows=num_rows,
            ),
            style = work_experience_stack_style,
        ),
        style = work_experience_style,
    )