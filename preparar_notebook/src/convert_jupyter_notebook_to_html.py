import os
import pathlib
import platform
import re
from check_for_new_classes import check_for_new_classes
from utils import get_portafolio_path
from format_code_blocks import format_code_blocks
from PIL import Image
import requests
from io import BytesIO
from img_base64 import base64_to_webp
from jupyter_notebook_to_html.jupyter_notebook_to_html import jupyter_notebook_contents_in_xml_format_to_html

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

CLOUDFLARE_HREF = "https://pub-fb664c455eca46a2ba762a065ac900f7.r2.dev/"

open_brace = "{"
closing_brace = "}"

link_img_counter = 0
webp_img_counter = 0

def add_index_html(html_content):
    index_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<h2" in line or "<h3" in line or "<h4" in line or "<h5" in line or "<h6" in line:
            line_to_add = line
            if "<h1" in line: tittle = "h1"
            elif "<h2" in line: tittle = "h2"
            elif "<h3" in line: tittle = "h3"
            elif "<h4" in line: tittle = "h4"
            elif "<h5" in line: tittle = "h5"
            elif "<h6" in line: tittle = "h6"
            
            # Check if the line has id and anchor link
            has_id = 'id="' in line
            has_anchor = '<a' in line
            
            if has_id and has_anchor:
                # Original logic for lines with id and anchor
                start_id_position = line.find('id="') + 4   # start id position is the position of `id="` in the line
                end_id_position = line.find('">')           # end id position is the position of `">` in the line
                start_anchor_position = line.find("<a")     # start anchor position is the position of `<a` in the line
                id = line[start_id_position:end_id_position]
                text = line[end_id_position+2:start_anchor_position]
            else:
                # Handle lines without id or anchor link
                # Extract text between opening and closing header tags
                start_tag_end = line.find('>') + 1
                end_tag_start = line.find(f'</{tittle}>')
                if start_tag_end > 0 and end_tag_start > 0:
                    text = line[start_tag_end:end_tag_start]
                    # Generate id from text, removing HTML tags for the href
                    id = re.sub(r'<[^>]+>', '', text).strip()
                else:
                    continue  # Skip if we can't parse the line properly
            
            index_html += f'      <a class="anchor-link" href="#{id}"><{tittle}>{text}</{tittle}></a>\n'
    return index_html

def add_content_html(html_content):
    global link_img_counter

    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<section class" in line:
            content_html += "      \n"
        if "¶" in line:
            line = line.replace("¶", f'<img decoding="async" class="link-img" width="24px" height="24px" alt="link image {link_img_counter}" src={open_brace}svg_paths.link_svg_path{closing_brace}/>')
            link_img_counter += 1
        content_html += f"      {line}\n"
    return content_html

def format_anchor_links(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<a" in line:
            # Get the position of the start and end of the open anchor
            start_open_anchor_position = None
            end_open_anchor_position = None
            for i in range(len(line)):
                if line[i:].startswith("<a"):
                    start_open_anchor_position = i     # start anchor position if the string starts with `<a` in the line
                    break
            if start_open_anchor_position is not None:
                for i in range(start_open_anchor_position, len(line)):
                    if line[i:].startswith("\">"):
                        end_open_anchor_position = i+1     # end anchor position if the string ends with `">` in the line
                        break
            if start_open_anchor_position is not None and end_open_anchor_position is not None:
                # Get href
                for i in range(start_open_anchor_position, end_open_anchor_position):
                    href = None
                    if line[i:].startswith("href"):
                        start_href_position = i + 6
                        end_href_position = end_open_anchor_position - 1
                        href = line[start_href_position:end_href_position]
                        external = False
                        break
                if href:
                    # Check if the href is internal or external
                    if ("http:" in href or "https:" in href or "www." in href) and not "maximofn.com" in href:
                        external = True
                    if href.startswith("#"):
                        external = False
                    
                    if external:
                        line = line[:start_open_anchor_position] + f'<a href="{href}" target="_blank" rel="nofollow noreferrer">' + line[end_open_anchor_position+1:]
        content_html += f"{line}\n"
    return content_html

def format_images(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<img" in line:
            # Get the position of the start and end of the img
            start_img_position = None
            end_img_position = None
            for i in range(len(line)):
                if line[i:].startswith("<img"):
                    start_img_position = i     # start img position if the string starts with `<img` in the line
                    break
            if start_img_position is not None:
                for i in range(start_img_position, len(line)):
                    if line[i:].startswith(">"):
                        end_img_position = i+1     # end img position if the string ends with `">` in the line
                        break
            if start_img_position is not None and end_img_position is not None:
                img_html_item = line[start_img_position:end_img_position]
                if "decoding" not in img_html_item:
                    line = line[:start_img_position+4] + ' decoding="async"' + line[start_img_position+4:]
        content_html += f"{line}\n"
    return content_html

def replace_braces(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    start_section_line = None
    end_section_line = None
    for number_line, line in enumerate(html_content_lines):
        if "<section" in line: # Start section
            start_section_line = number_line
            # Find the end of the section
            for i in range(number_line, len(html_content_lines)):
                if "</section" in html_content_lines[i]:
                    end_section_line = i
                    break
            # Replace the braces in the section
            if start_section_line is not None and end_section_line is not None:
                if start_section_line < end_section_line:
                    for i in range(start_section_line, end_section_line):
                        if '<p' in html_content_lines[i] or '<span' in html_content_lines[i]:
                            # First replace {opening_brace} by &$&%&$&%$$&%
                            html_content_lines[i] = html_content_lines[i].replace("{opening_brace}", "&$&%&$&%$$&%")
                            # Second replace {colsing_brace} by &$&%&$&%$$&#
                            html_content_lines[i] = html_content_lines[i].replace("{closing_brace}", "&$&%&$&%$$&#")
                            # Thirth replace { by &$&%&$&%$$&=
                            html_content_lines[i] = html_content_lines[i].replace("{", "&$&%&$&%$$&=")
                            # Fourth replace } by &$&%&$&%$$=&
                            html_content_lines[i] = html_content_lines[i].replace("}", "&$&%&$&%$$=&")

                            # Now replace &$&%&$&%$$&% by {opening_brace}, &$&%&$&%$$&# by {closing_brace}, &$&%&$&%$$&= by {opening_brace} and &$&%&$&%$$=& by {closing_brace}
                            html_content_lines[i] = html_content_lines[i].replace("&$&%&$&%$$&%", "{opening_brace}").replace("&$&%&$&%$$&#", "{closing_brace}").replace("&$&%&$&%$$&=", "{opening_brace}").replace("&$&%&$&%$$=&", "{closing_brace}")
        content_html += f"{html_content_lines[number_line]}\n"
    return content_html

def img_base64_to_webp(html_content, notebook_title):
    global webp_img_counter

    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<img" in line:
            start_src_position = None
            # Get src
            src = None
            for i in range(len(line)):
                if line[i:].startswith("src"):
                    start_src_position = i + 5
                    if line[start_src_position-1] != '"':
                            start_src_position = None
                    if start_src_position is not None:
                        end_src_position = line.find('"', start_src_position)
                        src = line[start_src_position:end_src_position]
                        break
            # Open image and get width and height
            if src is not None:
                if src.startswith("data:image"):
                    notebook_title_without_extension = notebook_title.split(".")[0]
                    image_name = notebook_title_without_extension + str(webp_img_counter) + ".webp"
                    base64_to_webp(src, image_name)
                    webp_img_counter += 1
                    line = f'      <img src="{CLOUDFLARE_HREF}{image_name}" alt="image {notebook_title_without_extension} {webp_img_counter}" loading="lazy">'
        content_html += f"{line}\n"
    return content_html

def format_cell_code_blocks(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    start_cell_code_block = None
    end_cell_code_block = None

    for i in range(len(html_content_lines)):
        if start_cell_code_block is not None and end_cell_code_block is not None:
            if i < end_cell_code_block:
                continue
            else:
                start_cell_code_block = None
                end_cell_code_block = None
        else:
            start_cell_code_block = None
            end_cell_code_block = None

        # Get the start and end of the cell code block
        if '<div class="highlight"><pre>' in html_content_lines[i]:
            start_cell_code_block = i
            for j in range(i, len(html_content_lines)):
                if '</pre></div>' in html_content_lines[j]:
                    end_cell_code_block = j+1
                    break
            
            if start_cell_code_block is not None and end_cell_code_block is not None:
                for k in range(start_cell_code_block, end_cell_code_block):
                    if '<div class="highlight"><pre>' in html_content_lines[k]:
                        content_html += '      <div class="highlight">\n'
                        lines_k = html_content_lines[k].replace('<div class="highlight"><pre>', '<pre>')
                        content_html += f"  {lines_k}</pre>\n"
                    elif '</pre></div>' in html_content_lines[k]:
                        content_html += '      </div>\n'
                    else:
                        # Get position of first character not space
                        position_first_character_not_space = None
                        for l in range(len(html_content_lines[k])):
                            if html_content_lines[k][l] != " ":
                                position_first_character_not_space = l
                                break
                        if position_first_character_not_space is not None:
                            lines_k = html_content_lines[k][position_first_character_not_space:]
                            spaces = " "*(l-6)
                            content_html += f"        <pre>{spaces}{lines_k}</pre>\n"
        
        else:
            content_html += f"{html_content_lines[i]}\n"
    
    return content_html

def add_witdh_and_height_to_image(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<img" in line:
            start_src_position = None
            # Get src
            src = None
            for i in range(len(line)):
                if line[i:].startswith("src"):
                    start_src_position = i + 5
                    if line[start_src_position-1] != '"':
                            start_src_position = None
                    if start_src_position:
                        end_src_position = line.find('"', start_src_position)
                        src = line[start_src_position:end_src_position]
                        break
            # Open image and get width and height
            if src:
                try:
                    with Image.open(BytesIO(requests.get(src).content)) as img:
                        width, height = img.size
                    # Add width and height into end_src_position position
                    line = line[:end_src_position+1] + f' width="{width}" height="{height}"' + line[end_src_position+1:]
                except Exception as e:
                    print(f"Error: {e}")
                    print(f"src: {src}")
                    if ".svg" in src:
                        pass
                    else:
                        print(f"Error: {e}")
                        print(f"src: {src}")
                        exit(1)
        content_html += f"{line}\n"
    return content_html

def remove_h1_from_html_content(html_content):
    content_html = ""
    html_content_lines = html_content.split("\n")
    for line in html_content_lines:
        if "<h1" in line:
            continue
        content_html += f"{line}\n"
    return content_html

def get_list_of_contents(xml_file_path: pathlib.Path) -> list[dict]:
    """
    Parse the XML file and return a list of contents maintaining the sequential order
    of markdown cells, code cells, and output cells as they appear in the notebook.
    
    Args:
        xml_file_path: Path to the XML file to parse
        
    Returns:
        list[dict]: List of dictionaries where each dict contains one cell type and content
    """
    list_of_contents = []
    
    try:
        with open(xml_file_path, 'r', encoding='utf-8') as xml_file:
            xml_content = xml_file.read()
            
            # Find the start and end of the content between <notebook> and </notebook>
            xml_start_content_char = re.search(r'<notebook>', xml_content).start() + len("<notebook>") + len("\n")
            xml_end_content_char = re.search(r'</notebook>', xml_content).end() - len("</notebook>") - len("\n")
            
            # Get the content between the start and end character positions
            xml_content_section_lines = xml_content[xml_start_content_char:xml_end_content_char].split("\n")

            # Convert the content of a list of dictionaries
            num_lines_content = len(xml_content_section_lines)
            for line_number in range(num_lines_content):
                # Get line content
                line = xml_content_section_lines[line_number]

                # Initialize start and end of item
                start_item_list_line = None
                end_item_list_line = None
                
                # Check if line is start of a new item
                if "<markdown>" in line or "<input_code>" in line or "<output_code>" in line:
                    start_item_list_line = line_number
                    if "<markdown>" in line:
                        item_type = "markdown"
                    elif "<input_code>" in line:
                        item_type = "input_code"
                    elif "<output_code>" in line:
                        item_type = "output_code"
                    else:
                        print(f"Error: {line} is not a valid item type")
                        exit(1)
                    
                    # Find the end of the item
                    for line_number_2 in range(start_item_list_line, num_lines_content):
                        if item_type == "markdown":
                            if "</markdown>" in xml_content_section_lines[line_number_2]:
                                end_item_list_line = line_number_2
                                break
                        elif item_type == "input_code":
                            if "</input_code>" in xml_content_section_lines[line_number_2]:
                                end_item_list_line = line_number_2
                                break
                        elif item_type == "output_code":
                            if "</output_code>" in xml_content_section_lines[line_number_2]:
                                end_item_list_line = line_number_2
                                break
                        else:
                            print(f"Error: {line} is not a valid item type")
                            exit(1)
                    
                    # Add the item to the list of contents
                    if start_item_list_line is not None and end_item_list_line is not None:
                        # Get list of lines of the item
                        item_list = xml_content_section_lines[start_item_list_line:min(end_item_list_line+1, num_lines_content)]
                        # Join the lines of the item
                        item_content = "\n".join(item_list)
                        # Get position on start and end of the type of the item
                        if item_type == "markdown":
                            start_item_type_position = item_content.find("<markdown>") + len("<markdown>")
                            end_item_type_position = item_content.find("</markdown>")
                        elif item_type == "input_code":
                            start_item_type_position = item_content.find("<input_code>") + len("<input_code>")
                            end_item_type_position = item_content.find("</input_code>")
                        elif item_type == "output_code":
                            start_item_type_position = item_content.find("<output_code>") + len("<output_code>")
                            end_item_type_position = item_content.find("</output_code>")
                        else:
                            print(f"Error: {item_content} is not a valid item type")
                            exit(1)
                        # Get the item content without the type
                        item_content = item_content[start_item_type_position:end_item_type_position]
                        # Create a dictionary with the item type and content
                        item_dict = {item_type: item_content}
                        # Add the item to the list of contents
                        list_of_contents.append(item_dict)
                
    except FileNotFoundError:
        print(f"Error: XML file not found at {xml_file_path}")
    except Exception as e:
        print(f"Error parsing XML file: {e}")
    
    return list_of_contents

def convert_jupyter_notebook_to_html(notebook_path, metadata, notebook_title):
    global webp_img_counter

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

    # Get metadata
    tittles_list = [metadata[0], metadata[1], metadata[2]]
    end_url = metadata[3]
    if end_url.endswith("/"):
        end_url = end_url[:-1]
    descriptions_list = [metadata[4], metadata[5], metadata[6]]
    keywords_list = [metadata[7], metadata[8], metadata[9]]
    image, image_hover_path, witdh, height, image_extension, date = metadata[10], metadata[11], metadata[12], metadata[13], metadata[14], metadata[15]

    # Detect the operating system
    system = platform.system()

    # Convert the notebooks to html
    for notebook_number, notebook in enumerate(notebook_paths):
        language = LANGUAJES_DICT[LANGUAGES[notebook_number]].upper()

        # Get list of contents
        xml_file = notebook_path.with_suffix(".xml")    # PosixPath('../posts/notebook_name.xml')
        # If language is ENGLISH ass _EN.xml, if language is PORTUGUESE ass _PT.xml
        if LANGUAGES[notebook_number] == ENGLISH:
            xml_file_path = xml_file.parent / "xml_files" / f"{xml_file.stem}_EN.xml"
        elif LANGUAGES[notebook_number] == PORTUGUESE:
            xml_file_path = xml_file.parent / "xml_files" / f"{xml_file.stem}_PT.xml"
        elif LANGUAGES[notebook_number] == SPANISH:
            xml_file_path = xml_file.parent / "xml_files" / f"{xml_file.stem}.xml"
        else:
            print(f"Error: {LANGUAGES[notebook_number]} is not a valid language")
            exit(1)
        list_of_jupyter_notebook_contents_in_xml_format = get_list_of_contents(xml_file_path)

        # Define the destiny path and name of the html file
        destiny_path = path / HTML_FILES
        destiny_name = notebook.stem + ".html"
        full_destiny_path = destiny_path / destiny_name

        # Choose the appropriate command based on the operating system
        try:
            if CONVERT_TO_HTML_WITH_NBCONVERT:
                if system == "Darwin":  # macOS
                    os.system(f"jupyter nbconvert --to html --template-file=/Users/macm1/miniforge3/share/jupyter/posts_template/index.html.j2 {notebook}")
                else:  # Linux/Ubuntu
                    os.system(f"jupyter nbconvert --to html --template posts_template {notebook}")
            else:
                print(f"Converting {notebook} to html...")

                # Convert the markdown content to html
                html_content = jupyter_notebook_contents_in_xml_format_to_html(list_of_jupyter_notebook_contents_in_xml_format)

                # Save the html content to the html file
                with open(full_destiny_path, 'w', encoding='utf-8') as html_file:
                    html_file.write(html_content)

        except Exception as e:
            print(f"Error: {e}")
            print(f"notebook: {notebook}")
            exit(1)

        # Move the generated html file to the destination path if CONVERT_TO_HTML_WITH_NBCONVERT is True
        if CONVERT_TO_HTML_WITH_NBCONVERT: 
            try:
                os.system(f"mv {notebook.with_suffix('.html')} {full_destiny_path}")
            except Exception as e:
                print(f"Error: {e}")
                print(f"notebook: {notebook}")
                exit(1)
    
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
const description = '{descriptions_list[notebook_number].replace("'", "\\'")}';
const keywords = '{keywords_list[notebook_number].replace("'", "\\'")}';
const languaje = '{LANGUAGES[notebook_number]}';
const image_path = '{image.replace("'", "\\'")}';
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

    <aside class=\"post-index\">
"""
        close_post_index="""    </aside>


"""
        post_content="""    <div class=\"post-body-content\">
"""
        botom_file="""
    </div>

  </section>

</PostLayout>
"""

        if CONVERT_TO_HTML_WITH_NBCONVERT:
            try:
                with open(full_destiny_path, 'r') as html_file:
                    html_content = html_file.read()
            except Exception as e:
                print(f"Error: {e}")
                print(f"full_destiny_path: {full_destiny_path}")
                exit(1)

        # write html_content to file
        index_html = add_index_html(html_content)
        html_content = html_content.replace('<img', '<img onerror="this.parentNode.removeChild(this)"')
        content_html = add_content_html(html_content)
        content_html = content_html.replace('<div class="highlight hl-ipython3">', '<div class="highlight hl-ipython3">\n')
        content_html = format_code_blocks(content_html)
        content_html = content_html.replace('\n      </code></pre>', '</code></pre>')
        content_html = format_anchor_links(content_html)
        content_html = format_images(content_html)
        content_html = replace_braces(content_html)
        content_html = img_base64_to_webp(content_html, notebook_title)
        content_html = format_cell_code_blocks(content_html)
        webp_img_counter = 0
        content_html = remove_h1_from_html_content(content_html)

        with open(astro_file_path, 'w') as astro_file:
            astro_file.write(header_file)
            astro_file.write(post_index)
            astro_file.write(index_html)
            astro_file.write(close_post_index)
            astro_file.write(post_content)
            astro_file.write(content_html)
            astro_file.write(botom_file)
        print("Done")
