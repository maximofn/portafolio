from fasthtml.common import *
import header
import colors
import links
import projects
import posts

debug = False

app, rt = fast_app(live=True, default_hdrs=False)

max_width = 1500


###################### ABOUT ME ######################
def about_me_info():
    style = 'outline: 1px solid blue;' if debug else ''
    style += 'margin: 10px 0px'

    return Div(
        H2("Sobre mi"),
        H1("MaximoFN"),
        H2("¿Quieres aprender inteligencia artificial?"),
        P("Soy Máximo Fernández y mi objetivo es ayudar a la gente a aprender Inteligencia Artificial publicando contenido en español."),
        P("Entra y aprende todo lo que puedas"),
        style=style,
    )

def about_me_photo():
    style = 'outline: 1px solid blue;' if debug else ''
    width = 291
    height = 436
    style += f'width: {width}px; height: {height}px;'

    return Img(
        src=links.maximofn_photo_path,
        alt="MaximoFN",
        cls="home-img",
        style=style,
    ),

def about_me():
    style = 'outline: 1px solid green;' if debug else ''
    style += 'display: flex; flex-direction: row; flex-srink: 0;'
    style += 'justify-content: space-around;'
    style += 'align-items: flex-end;'
    style += 'gap: 10px;'
    style += f'max-width: {max_width}px;'
    style += 'width: 100%;'

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

    style_projects_cards_div = 'outline: 1px solid blue;' if debug else ''
    style_projects_cards_div += 'display: flex;'
    style_projects_cards_div += 'flex-direction: row;'
    style_projects_cards_div += 'justify-content: space-around;'

    return Section(
        H2("Proyectos"),
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

    return Section(
        H2("Ultimos posts"),
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
    background_color = colors.colors['950']
    style += f'background-color: {background_color};'
    style += 'width: 100%;'
    style += 'display: flex;'
    style += 'flex-direction: column;'
    style += 'justify-content: flex-start;'
    style += 'align-items: center;'
    style += 'gap: 20px;'
    style += 'color: white;'    # font color

    return Container(
        header.header(),
        about_me(),
        projects_section(),
        posts_section(),
        Footer("Footer"),

        style=style,
    )

serve()
