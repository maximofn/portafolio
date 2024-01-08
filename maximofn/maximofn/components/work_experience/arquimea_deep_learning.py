import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def arquimea_deep_learning(row_start: int, row_end: int, column: int) -> rx.Component:
    return custom_work_experience(
        company = "Arqimea",
        position = "Ingeniero de deep learning",
        date_start = "Agosto 2019",
        date_end = "Julio 2022",
        responsabilities = [
            "Algoritmos de visión por ordenador. Investigación y desarrollo de pruebas de concepto e introducción de nuevas tecnologías al equipo.",
            "Electrónica UAV: Liderando nuevos diseños tanto HW como FW. Elegir a las personas adecuadas para realizarlos y explicarles los conceptos.",
            "Servir de mentor a otros para acelerar su crecimiento profesional y animarles a participar.",
            "Cuestionar los procesos del equipo, buscando formas de mejorarlos.",
        ],
        key_accomplishments = [
            "Introduje el procesamiento de vídeo en el UAV, haciendo de esta nueva funcionalidad un valor añadido y diferenciándonos de la competencia.",
            "Desarrollé los algoritmos de visión de forma que se descartara el uso de dispositivos comerciales que cuestan 2.000 € por unidad. Esto supone un gran ahorro por UAV, por lo que pueden venderse más baratos y destacar en el mercado.",
            "Gracias a un prototipo que se geoposiciona sin GPS, se ha abierto una nueva línea de investigación para futuros UAV para la guerra tecnológica.",
        ],
        row_start=row_start,
        row_end=row_end,
        column=column,
    )