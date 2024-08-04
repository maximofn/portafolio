from fasthtml.common import *
import header
import links
import projects
import posts
import styles
import colors

debug = False
sticky_top = 100

hdrs = (
    Title("MaximoFN"),
    Meta(charset="UTF-8"),
    Meta(name="viewport", content="width=device-width, initial-scale=1"),
    Meta(name="description", content="Página de MaximoFN. Página para aprender sobre IA en español"),
    Meta(name="keywords", content="IA, Inteligencia Artificial, Python, Español"),
    Meta(name="author", content="MaximoFN"),
    Meta(name="robots", content="index, follow"),
    Meta(name="theme-color", content=f"{colors.colors['950']}"),
    Link(rel="icon", href=links.logo_path),
    # Open Graph / Facebook
    Meta(property="og:type", content="website"),
    Meta(property="og:url", content="https://maximofn.com"),
    Meta(property="og:title", content="MaximoFN"),
    Meta(property="og:description", content="Página de MaximoFN. Página para aprender sobre IA en español"),
    Meta(property="og:image", content=links.maximofn_photo_path),
    Meta(property="og:image:alt", content="MaximoFN"),
    # Twitter
    Meta(property="twitter:card", content="summary_large_image"),
    Meta(property="twitter:url", content="https://maximofn.com"),
    Meta(property="twitter:title", content="MaximoFN"),
    Meta(property="twitter:description", content="Página de MaximoFN. Página para aprender sobre IA en español"),
    Meta(property="twitter:image", content=links.maximofn_photo_path),
    # Style(styles.cascadia_font),
)

app, rt = fast_app(
    html_attrs={'lang': 'es'},
    live=True,
    default_hdrs=False,
    hdrs=hdrs,
)

max_width = 1500


###################### ABOUT ME ######################
def about_me_info():
    style = 'outline: 1px solid blue;' if debug else ''
    style += 'margin: 10px 0px'

    return Div(
        H2("Sobre mi"),
        H1("MaximoFN"),
        H2(
            "¿Quieres aprender ",
            Strong("inteligencia artificial"),
            "?",
        ),
        P("Soy Máximo Fernández y mi objetivo es ayudar a la gente a aprender Inteligencia Artificial publicando contenido en español."),
        P("Entra y aprende todo lo que puedas"),
        style=style,
    )

def about_me_photo():
    style = 'outline: 1px solid blue;' if debug else ''
    width = 291
    # height = 436
    style += f'max-width: {width}px; height: auto; width: 100%;'

    return Img(
        src=links.maximofn_photo_path,
        alt="MaximoFN",
        cls="home-img",
        style=style,
    ),

def about_me():
    style = 'outline: 1px solid green;' if debug else ''
    style += 'display: flex;'
    style += 'flex-direction: row;'
    style += 'flex-wrap: wrap;'
    style += 'flex-flow: row wrap-reverse;'
    # style += 'flex-srink: 0;'
    style += 'justify-content: space-around;'
    style += 'align-items: flex-end;'
    style += 'gap: 10px;'
    style += f'max-width: {max_width}px;'
    style += 'width: 100%;'
    style += 'background-color: transparent;'

    return Section(
        about_me_info(),
        about_me_photo(),
        style=style,
    )
#####################################################

###################### PROJECTS #####################
def projects_section():
    style_projects_section = 'outline: 1px solid green;' if debug else ''
    style_projects_section += 'display: flex;'
    style_projects_section += 'flex-direction: column;'
    style_projects_section += 'justify-content: space-between;'
    style_projects_section += 'gap: 10px;'
    style_projects_section += f'max-width: {max_width}px;'
    style_projects_section += 'width: 100%;'
    style_projects_section += 'position: relative;'

    style_projects_cards_div = 'outline: 1px solid blue;' if debug else ''
    style_projects_cards_div += 'display: flex;'
    style_projects_cards_div += 'flex-direction: row;'
    style_projects_cards_div += 'flex-wrap: wrap;'
    style_projects_cards_div += 'gap: 10px;'
    style_projects_cards_div += 'justify-content: space-around;'

    return Section(
        H2(
            "Proyectos",
            style = f"position: sticky; top: {sticky_top}px;"
        ),
        Div(
            projects.project_card(
                title='Proyecto 1',
                description='Descripción del proyecto 1',
                img_path=links.default_project_image_path,
                project_link='https://www.google.com',
                code_link='https://www.google.com',
            ),
            projects.project_card(
                title='Proyecto 2',
                description='Descripción del proyecto 2',
                img_path=links.default_project_image_path,
                project_link='https://www.google.com',
            ),
            projects.project_card(
                title='Proyecto 3',
                description='Descripción del proyecto 3',
                img_path=links.default_project_image_path,
            ),
            style=style_projects_cards_div,
        ),
        A('Todos los proyectos -->', href='https://www.google.com'),
        style=style_projects_section,
    )
#####################################################

###################### POSTS #######################
def posts_section():
    style_posts_section = 'outline: 1px solid green;' if debug else ''
    style_posts_section += 'display: flex;'
    style_posts_section += 'flex-direction: column;'
    style_posts_section += 'justify-content: space-between;'
    style_posts_section += 'gap: 10px;'
    style_posts_section += f'max-width: {max_width}px;'
    style_posts_section += 'width: 100%;'
    style_posts_section += 'position: relative;'

    return Section(
        H2(
            "Ultimos posts",
            style = f"position: sticky; top: {sticky_top}px;"
        ),
        posts.post_card(
            title='Post 1',
            description='Descripción del post 1',
            img_path=links.default_project_image_path,
            post_link='https://www.google.com',
        ),
        posts.post_card(
            title='Post 2',
            description='Descripción del post 2',
            img_path=links.default_project_image_path,
            post_link='https://www.google.com',
        ),
        posts.post_card(
            title='Post 3',
            description='Descripción del post 3',
            img_path=links.default_project_image_path,
            post_link='https://www.google.com',
        ),
        A('Todos los posts -->', href='https://www.google.com'),
        style=style_posts_section,
    )
#####################################################

@rt('/')
def get():
    style = 'outline: 1px solid red;' if debug else ''
    style += 'display: flex;'
    style += 'flex-direction: column;'
    style += 'justify-content: flex-start;'
    style += 'align-items: center;'
    style += 'gap: 20px;'
    style += 'margin: 0px;'
    style += 'padding: 0px;'

    style += styles.font

    grid_stye = ''
    if True:
    # if dark_mode:
        style += styles.dark_background
        grid_stye += styles.dark_background_grid
    else:
        style += styles.light_background
        grid_stye += styles.light_background_grid

    max_width = 300
    main_style = 'outline: 1px solid yellow;' if debug else ''
    main_style += 'display: flex;'
    main_style += 'flex-direction: column;'
    main_style += 'justify-content: flex-start;'
    main_style += 'align-items: center;'
    main_style += 'gap: 20px;'
    main_style += f'max-width: {max_width}px; height: auto; width: 100%;'

    

    return Body(
        header.header(),
        Main(
            about_me(),
            projects_section(),
            posts_section(),
            style="position: relative;",
        ),
        Footer("Footer"),
        Section(style=styles.dark_background_grid),
        style=style,
    )

serve()
