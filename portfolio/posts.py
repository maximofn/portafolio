from fasthtml.common import *

debug = False

def post_card(title, description, img_path, post_link):
    card_style = 'outline: 1px solid yellow;' if debug else ''
    card_style += 'display: flex;'
    card_style += 'flex-direction: row;'
    card_style += 'justify-content: flex-start;'
    card_style += 'align-items: flex-start;'
    card_style += 'gap: 10px;'

    content_style = 'outline: 1px solid red;' if debug else ''
    content_style += 'display: flex;'
    content_style += 'flex-direction: column;'
    content_style += 'justify-content: center;'
    content_style += 'width: 100%;'

    image_style = 'width: 200px; height: 200px;'

    content = Div(
        A(H3(title), href=post_link),
        P(description),
        style=content_style,
    )

    return Article(
        A(
            Img(
                src=img_path,
                alt=title,
                loading='lazy',
                style=image_style,
            ),
            href=post_link,
        ),
        content,
        style=card_style,
    )
