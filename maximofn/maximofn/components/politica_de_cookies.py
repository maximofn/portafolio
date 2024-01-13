import reflex as rx

from maximofn.styles.colors import Color
from maximofn.styles.page_style import page_style

from maximofn.components.header import header
from maximofn.components.footer import footer

def politica_de_cookies() -> rx.Component:
    return rx.vstack(
        header(),
        rx.vstack(
            rx.heading(
                "Consideraciones previas",
                font_color = Color.WHITE.value,
            ),
            rx.text(
                "Se entenderá por usuario toda persona que navegue en el sitio web https://maximofn.com en lo adelante, simplemente el sitio web."
            ),
            rx.text(
                "Se entenderá por editor el dueño del sitio web, quien es Máximo Fernández Núñez y está identificado en el aviso legal."
            ),
            rx.text(
                "Las cookies utilizadas en el navegador del usuario se han instalado con su autorización. Si en algún momento desea revocar esta autorización, podrá hacerlo sin obstáculo alguno. Para ello puede visualizar la sección Desactivación o eliminación de cookies, que se encuentra descrita en estas políticas."
            ),
            rx.text(
                "El Editor está en total libertad de realizar los cambios que considere pertinentes en el sitio web. Para ello podrá añadir apartados, funcionalidades o cualquier elemento que quizás pueda generar el uso de nuevas cookies, por lo que se aconseja al usuario que verifique la presente política de cookies cada vez que acceda al sitio web, para que pueda mantenerse actualizado por cualquier cambio que se pueda haber dado desde la última visita realizada."
            ),

            rx.heading(
                "Definición y función de las cookies",
                font_color = Color.WHITE.value,
            ),
            rx.text(
                "Las cookies son informaciones que se almacenan en el navegador del usuario de un sitio web para poder consultar la actividad previa que ha tenido, así como recordar ciertos datos para una próxima visita. También pueden ser llamadas web beacons, píxel, bugs, rastreadores, pero a efectos de estas políticas, se entenderán solamente como cookies."
            ),
            rx.text(
                "Suelen almacenar datos de carácter técnico, estadísticas de uso, personalización de perfiles, enlaces a redes sociales, administración de preferencias personales, entre otras funciones, con el fin de poder adaptar el sitio web a las necesidades y configuraciones del usuario, mejorando así la experiencia de la navegación, el no aceptarlas podría entorpecer el servicio que el sitio web desea ofrecer."
            ),
            rx.text(
                "No son archivos de virus, spam, troyanos, gusanos, spyware, ni programación publicitaria ya sea estática en la página o en formato de ventana emergente (pop-up)."
            ),
            rx.text(
                "La información almacenada se refiere al navegador (Internet Explorer, Safari, Chrome, Firefox, etc.), y no al usuario, para constatar esto puede entrar en el mismo dominio web y verificar en dos navegadores diferentes que puede configurar diferentes preferencias en cada uno."
            ),

            background_color = Color.BACKGROUND.value,
            font_color = Color.WHITE.value,
        ),
        footer(),
        style=page_style,
    )