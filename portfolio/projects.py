from fasthtml.common import *

debug = False

def view_button(link):
    return Button('Ver', href=link)

def code_button(link):
    return Button('Código', href=link)

def project_card(title, description, img_path, project_link=None, code_link=None):
    style = 'outline: 1px solid yellow;' if debug else ''
    style += 'display: flex;'
    style += 'flex-direction: column;'
    style += 'justify-content: flex-start;'
    style += 'align-items: center;'

    max_width = 400
    image_style = f'max-width: {max_width}px; height: auto; width: 100%;'

    project_card_tuple = (
        H3(title),
        Img(
            src=img_path,
            alt=title,
            style=image_style,
        ),
        P(description),
    )
    if project_link and code_link:
        project_card_tuple += (Div(
            view_button(project_link),
            code_button(code_link),
            style='display: flex; gap: 10px;'
        ),)
    else:
        if project_link:
            project_card_tuple += (view_button(project_link),)
        if code_link:
            project_card_tuple += (code_button(code_link),)

    return Article(
        project_card_tuple,
        style=style,
    )
