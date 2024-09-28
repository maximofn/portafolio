import os
import pathlib
from check_for_new_classes import check_for_new_classes
from utils import get_portafolio_path
from format_code_blocks import format_code_blocks

CONVERT_TO_HTML_WITH_NBCONVERT = False

HTML_FILES = "html_files"
NOTEBOOKS_TRANSLATED = "notebooks_translated"
ASTRO_SRC_PAGES = "portfolio/src/pages"
ASTRO_SRC_PAGES_EN = "portfolio/src/pages/en"
ASTRO_SRC_PAGES_PT = "portfolio/src/pages/pt-br"
SPANISH = "ES"
ENGLISH = "EN"
PORTUGUESE = "PT"
LANGUAGES = [SPANISH, ENGLISH, PORTUGUESE]
LANGUAJES_DICT = {SPANISH: "spanish", ENGLISH: "english", PORTUGUESE: "portuguese"}

open_brace = "{"
closing_brace = "}"

def add_index_html(html_content):
    index_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<h2" in line or "<h3" in line or "<h4" in line or "<h5" in line or "<h6" in line:
            if "<h1" in line: tittle = "h1"
            elif "<h2" in line: tittle = "h2"
            elif "<h3" in line: tittle = "h3"
            elif "<h4" in line: tittle = "h4"
            elif "<h5" in line: tittle = "h5"
            elif "<h6" in line: tittle = "h6"
            start_id_position = line.find('id="') + 4   # start id position is the position of `id="` in the line
            end_id_position = line.find('">')           # end id position is the position of `">` in the line
            start_anchor_position = line.find("<a")     # start anchor position is the position of `<a` in the line
            id = line[start_id_position:end_id_position]
            text = line[end_id_position+2:start_anchor_position]
            index_html += f'      <a class="anchor-link" href="#{id}"><{tittle}>{text}</{tittle}></a>\n'
    return index_html

def add_content_html(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<section class" in line:
            content_html += "      \n"
        if "¶" in line:
            line = line.replace("¶", f'<img decoding="async" class="link-img" alt="link-svg" src={open_brace}svg_paths.link_svg_path{closing_brace}/>')
        content_html += f"      {line}\n"
    return content_html

def convert_to_html(notebook_path, metadata):
    # Get path, name and extension of the notebook
    notebook_path = pathlib.Path(notebook_path)
    path = notebook_path.parent
    notebook_name = notebook_path.stem
    notebook_extension = notebook_path.suffix

    # Get scritp path
    script_path = pathlib.Path(__file__).parent

    # Create the paths for the translated notebooks
    notebook_name_en = notebook_name + "_" + ENGLISH + notebook_extension
    notebook_name_pt = notebook_name + "_" + PORTUGUESE + notebook_extension
    notebook_paths = [notebook_path, path/NOTEBOOKS_TRANSLATED/notebook_name_en, path/NOTEBOOKS_TRANSLATED/notebook_name_pt]
    astro_src_pages_list = [ASTRO_SRC_PAGES, ASTRO_SRC_PAGES_EN, ASTRO_SRC_PAGES_PT]
    # title_es, title_en, title_pt, end_url, description_es, description_en, description_pt, \
    # keywords_es, keywords_en, keywords_pt, image, witdh, height, image_extension, date
    tittles_list = [metadata[0], metadata[1], metadata[2]]
    end_url = metadata[3]
    descriptions_list = [metadata[4], metadata[5], metadata[6]]
    keywords_list = [metadata[7], metadata[8], metadata[9]]
    image, witdh, height, image_extension, date = metadata[10], metadata[11], metadata[12], metadata[13], metadata[14]

    # Convert the notebooks to html
    for notebook_number, notebook in enumerate(notebook_paths):
        language = LANGUAJES_DICT[LANGUAGES[notebook_number]].upper()

        # Execute the following command in the terminal: jupyter nbconvert --to html --template posts_template self.notebook_path
        if CONVERT_TO_HTML_WITH_NBCONVERT: os.system(f"jupyter nbconvert --to html --template posts_template {notebook}")

        # Move the generated html file to the destination path
        destiny_path = path / HTML_FILES
        destiny_name = notebook.stem + ".html"
        full_destiny_path = destiny_path / destiny_name
        if CONVERT_TO_HTML_WITH_NBCONVERT: os.system(f"mv {notebook.with_suffix('.html')} {full_destiny_path}")
    
        # Find for new classes in the generated html files
        print(f"\tChecking for new classes for {language}...", end=" ")
        check_for_new_classes(full_destiny_path)
        print("Done")

        # Create astro file with html file path content
        print(f"\tCreating astro file for {language}...", end=" ")
        portafolio_path = pathlib.Path(get_portafolio_path(script_path))
        astro_file_path = portafolio_path / astro_src_pages_list[notebook_number]
        astro_file_name = end_url + ".astro"
        astro_file_path = astro_file_path / astro_file_name
        
        header_file=f"""---
import PostLayout from '@layouts/PostLayout.astro';
import CodeBlockInputCell from '@components/CodeBlockInputCell.astro';
import CodeBlockOutputCell from '@components/CodeBlockOutputCell.astro';

const {open_brace} metadata_page {closing_brace} = await import('@portfolio/consts.json');
const {open_brace} colors {closing_brace} = await import('@portfolio/consts.json');
const {open_brace} svg_paths {closing_brace} = await import('@portfolio/consts.json');

const page_title = '{tittles_list[notebook_number]}';
const end_url = '{end_url}';
const description = '{descriptions_list[notebook_number]}';
const keywords = '{keywords_list[notebook_number]}';
const languaje = '{LANGUAGES[notebook_number]}';
const image_path = '{image}';
const opening_brace = '{open_brace}';
const closing_brace = '{closing_brace}';
---

<PostLayout 
    title={open_brace}page_title{closing_brace}
    languaje={open_brace}languaje{closing_brace}
    description={open_brace}description{closing_brace}
    keywords={open_brace}keywords{closing_brace}
    author={open_brace}metadata_page.author{closing_brace}
    theme_color={open_brace}colors.background_color{closing_brace}
    end_url={open_brace}end_url{closing_brace}
    image_path={open_brace}image_path{closing_brace}
    image_width={witdh}
    image_height={height}
    image_extension={image_extension}
    article_date={date}+T00:00:00Z
>

  <section class=\"post-body\">
"""
        post_index="""

    <div class=\"post-index\">
"""
        close_post_index="""    </div>


"""
        post_content="""    <div class=\"post-body-content\">
"""
        botom_file="""
    </div>

  </section>

</PostLayout>
"""

        with open(full_destiny_path, 'r') as html_file:
            html_content = html_file.read()
        index_html = add_index_html(html_content)
        content_html = add_content_html(html_content)
        content_html = content_html.replace('<div class="highlight hl-ipython3">', '<div class="highlight hl-ipython3">\n')
        content_html = format_code_blocks(content_html)
        content_html = content_html.replace('\n      </code></pre>', '</code></pre>')

        with open(astro_file_path, 'w') as astro_file:
            astro_file.write(header_file)
            astro_file.write(post_index)
            astro_file.write(index_html)
            astro_file.write(close_post_index)
            astro_file.write(post_content)
            astro_file.write(content_html)
            astro_file.write(botom_file)
        print("Done")
