import reflex as rx
from maximofn.components.work_experience.custom_work_experience import custom_work_experience

def sener() -> rx.Component:
    return custom_work_experience(
        company = "Sener Aeroespacial",
        position = "Ingeniero de deep learning",
        date_start = "Julio 2022",
        date_end = "Actual",
        responsabilities = [
            "Desarrollo de un conjunto de datos de imágenes sintéticas creadas con stable diffusion para entrenar redes de segmentación.",
            "Desarrollo de una arquitectura de red neuronal para la percepción por visión computerizada de vehículos terrestres en entornos no estructurados.",
            "Optimizar la máquina en la que se ejecutarán todos los algoritmos de percepción y guiado.",
            "Liderar el grupo de inteligencia artificial, para realizar tareas de visión en el dispositivo, el reentrenamiento de las redes y el procesamiento de datos.",
        ],
        key_accomplishments = [
            "Optimización de modelos con TensorRT, reduciendo el tiempo de inferencia y la memoria VRAM.",
            "Compartí mis conocimientos con el grupo, para capacitarlos para crear mejores soluciones juntos y más rápido.",
            "Mentor de becarios para que crecer profesionalmente.",
        ],
    )