import argparse
import pathlib
from get_notebook_metadata import get_notebook_metadata, check_if_notebook_metadata_is_ok, get_portafolio_path
from corrections_jupyter_notebook import ortografic_corrections_jupyter_notebook
from translate_jupyter_notebooks import translate_jupyter_notebook
from error_codes import QUOTA_EXCEEDED_ERROR
from convert_jupyter_notebook_to_html import convert_jupyter_notebook_to_html
from jupyter_notebook_to_xml import convert_notebook_to_xml
from add_page_to_its_json_file import add_page_to_its_json_file_from_metadata
from add_page_to_its_sitemap import add_page_to_its_sitemap_from_metadata
import json
from utils import ask_for_something

def parse_args():
    parser = argparse.ArgumentParser(description='Preparar notebook')
    parser.add_argument('file', type=str, help='File to prepare')   # Writing `file` and not `--file` makes that the argument is positional. It's not necessary to write `--file` when calling the script
    parser.add_argument('--no_check_metadata', action='store_true', help='Do not check if metadata is ok')
    parser.add_argument('--no_correct_ortografic_errors', action='store_true', help='Do not correct ortografic errors')
    parser.add_argument('--yes_correct_ortografic_errors', action='store_true', help='Correct ortografic errors')
    parser.add_argument('--no_translate', action='store_true', help='Do not translate the notebook')
    parser.add_argument('--yes_translate', action='store_true', help='Translate the notebook')
    parser.add_argument('--no_convert_to_xml', action='store_true', help='Do not convert the notebook to xml')
    parser.add_argument('--yes_convert_to_xml', action='store_true', help='Convert the notebook to xml')
    parser.add_argument('--no_convert_to_html', action='store_true', help='Do not convert the notebook to html')
    parser.add_argument('--yes_convert_to_html', action='store_true', help='Convert the notebook to html')
    parser.add_argument('--no_add_to_json', action='store_true', help='Do not add the astro metadata to the json file')
    parser.add_argument('--yes_add_to_json', action='store_true', help='Add the astro metadata to the json file')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    notebook_path = pathlib.Path(args.file)
    no_check_metadata = args.no_check_metadata
    no_correct_ortografic_errors = args.no_correct_ortografic_errors
    yes_correct_ortografic_errors = args.yes_correct_ortografic_errors
    no_translate = args.no_translate
    yes_translate = args.yes_translate
    no_convert_to_xml = args.no_convert_to_xml
    yes_convert_to_xml = args.yes_convert_to_xml
    no_convert_to_html = args.no_convert_to_html
    yes_convert_to_html = args.yes_convert_to_html
    no_add_to_json = args.no_add_to_json
    yes_add_to_json = args.yes_add_to_json

    # Get metadata from notebook
    notebook_metadata = get_notebook_metadata(notebook_path)

    # Check if metadata is ok
    if not no_check_metadata:
        if check_if_notebook_metadata_is_ok(notebook_metadata):
            print("Metadata is ok")
    
    # Correct ortographic errors
    if not no_correct_ortografic_errors:
        if yes_correct_ortografic_errors:
            print("Correcting ortographic errors")
            # Get corrections from gemini and save them in a json if there aren't corrections json file
            ortografic_corrections_jupyter_notebook(notebook_path)
        else:
            if ask_for_something("\nDo you want correct ortographic errors? (y/n)", ['y', 'yes'], ['n', 'no']):
                # Get corrections from gemini and save them in a json if there aren't corrections json file
                ortografic_corrections_jupyter_notebook(notebook_path)

    # Translate notebook
    if not no_translate:
        if yes_translate:
            print("Translating notebook")
            # Translate notebook
            translate_jupyter_notebook(notebook_path)
        else:
            if ask_for_something("\nDo you want to translate the notebook? (y/n)", ['y', 'yes'], ['n', 'no']):
                # Translate notebook
                translate_jupyter_notebook(notebook_path)
    
    # Convert to XML
    if not no_convert_to_xml:
        if yes_convert_to_xml:
            print("Converting to XML")
            # Convert to XML
            convert_notebook_to_xml(notebook_path)
        else:
            if ask_for_something("\nDo you want to convert the notebook to xml? (y/n)", ['y', 'yes'], ['n', 'no']):
                print("Converting to XML")
                # Convert to XML
                convert_notebook_to_xml(notebook_path)
    
    # Convert to HTML
    if not no_convert_to_html:
        if yes_convert_to_html:
            print("\nConverting to HTML")
            notebook_title = notebook_metadata[3]
            convert_jupyter_notebook_to_html(notebook_path, notebook_metadata, notebook_title)
        else:
            if ask_for_something("\nDo you want to convert the notebook to html? (y/n)", ['y', 'yes'], ['n', 'no']):
                print("\nConverting to HTML")
                notebook_title = notebook_metadata[3]
                convert_jupyter_notebook_to_html(notebook_path, notebook_metadata, notebook_title)

    # Add to json
    if not no_add_to_json:
        if yes_add_to_json:
            print("\nAdding to json")
            add_page_to_its_json_file_from_metadata(notebook_metadata, notebook_path)
        else:
            if ask_for_something("\nDo you want to add the astro metadata to the json file? (y/n)", ['y', 'yes'], ['n', 'no']):
                print("\nAdding to json")
                add_page_to_its_json_file_from_metadata(notebook_metadata, notebook_path)
