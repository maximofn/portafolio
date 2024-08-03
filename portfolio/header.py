from fasthtml.common import *
import links

debug = False

def home_link():
    style = 'outline: 1px solid red;' if debug else ''
    style += 'font-size: 1.5em'
    width = 50
    height = 50
    return A(
        Img(
            src=links.logo_path,
            alt="MaximoFN",
            cls="home-img",
            style=f'width: {width}px; height: {height}px;',),
        href='/',
        style=style,
    )

def social_link(img_path, img_alt, link):
    style = 'outline: 1px solid yellow;' if debug else ''
    width = 20
    height = 20
    image = Img(
        src=img_path,
        alt=img_alt,
        style=f'width: {width}px; height: {height}px;',
    )
    return A(
        image,
        href=link,
        style=style,
        target='_blank',
    )

def county_flag(img_path, img_alt):
    style = 'outline: 1px solid yellow;' if debug else ''
    style += 'margin: 0px 1px;'
    width = 20
    height = 20
    image = Img(
        src=img_path,
        alt=img_alt,
        style=f'width: {width}px; height: {height}px;',
    )
    return image

def social_links():
    style = 'outline: 1px solid red;' if debug else ''
    style += 'display: flex; align-items: center;'
    style += 'gap: 1px;'
    return Nav(
        social_link(
            img_path=links.huggingface_svg_path,
            img_alt='HuggingFace',
            link=links.huggingface_link,
        ),
        social_link(
            img_path=links.github_svg_path,
            img_alt='GitHub',
            link=links.github_link,
        ),
        social_link(
            img_path=links.linkedin_svg_path,
            img_alt='LinkedIn',
            link=links.linkedin_link,
        ),
        social_link(
            img_path=links.x_svg_path,
            img_alt='X',
            link=links.x_link,
        ),
        social_link(
            img_path=links.kaggle_svg_path,
            img_alt='Kaggle',
            link=links.kaggle_link,
        ),
        social_link(
            img_path=links.facebook_svg_path,
            img_alt='Facebook',
            link=links.facebook_link,
        ),
        social_link(
            img_path=links.instagram_svg_path,
            img_alt='Instagram',
            link=links.instagram_link,
        ),
        social_link(
            img_path=links.tiktok_svg_path,
            img_alt='TikTok',
            link=links.tiktok_link,
        ),
        social_link(
            img_path=links.twitch_svg_path,
            img_alt='Twitch',
            link=links.twitch_link,
        ),
        social_link(
            img_path=links.youtube_svg_path,
            img_alt='Youtube',
            link=links.youtube_link,
        ),
        social_link(
            img_path=links.curriculum_svg_path,
            img_alt='Curriculum',
            link=links.curriculum_link,
        ),
        style=style,
    )

def countries_flags():
    style = 'outline: 1px solid red;' if debug else ''
    style += 'display: flex; align-items: center;'
    style += 'gap: 2px;'
    return Nav(
        county_flag(
            img_path=links.spain_flag_svg_path,
            img_alt='Spain',
        ),
        county_flag(
            img_path=links.united_states_flag_svg_path,
            img_alt='United States',
        ),
        county_flag(
            img_path=links.brazil_flag_svg_path,
            img_alt='Brazil',
        ),
        style=style,
    )

def right_header():
    style = 'outline: 1px solid blue;' if debug else ''
    style += 'display: flex; flex-direction: row; flex-wrap: wrap; justify-content: flex-end;'
    style += 'gap: 10px;'
    style += 'align-items: center;'
    return Div(
        social_links(),
        countries_flags(),
        id='right-header',
        style=style,
    ),

def header():
    style = 'outline: 1px solid green;' if debug else ''
    style += 'display: flex; justify-content: space-between;'
    style += 'align-items: center;'
    style += 'width: 99%;'

    return Header(
        home_link(),
        right_header(),
        id='header',
        style=style,
    )