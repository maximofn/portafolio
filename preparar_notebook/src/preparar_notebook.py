import argparse
import pathlib
from get_notebook_metadata import get_notebook_metadata, check_if_notebook_metadata_is_ok, get_portafolio_path
from corrections_jupyter_notebook import ortografic_corrections_jupyter_notebook
from translate_jupyter_notebooks import translate_jupyter_notebook
from error_codes import QUOTA_EXCEEDED_ERROR
from jupyter_notebook_to_html import convert_to_html
from add_page_to_its_json_file import add_page_to_its_json_file_from_metadata
from add_page_to_its_sitemap import add_page_to_its_sitemap_from_metadata
import json
from utils import ask_for_something

def parse_args():
    parser = argparse.ArgumentParser(description='Preparar notebook')
    parser.add_argument('file', type=str, help='File to prepare')   # Writing `file` and not `--file` makes that the argument is positional. It's not necessary to write `--file` when calling the script
    parser.add_argument('--no_check_metadata', action='store_true', help='Do not check if metadata is ok')
    parser.add_argument('--no_correct_ortografic_errors', action='store_true', help='Do not correct ortografic errors')
    parser.add_argument('--no_translate', action='store_true', help='Do not translate the notebook')
    parser.add_argument('--no_convert_to_html', action='store_true', help='Do not convert the notebook to html')
    parser.add_argument('--no_add_to_json', action='store_true', help='Do not add the astro metadata to the json file')
    parser.add_argument('--no_add_to_sitemap', action='store_true', help='Do not add the astro metadata to the sitemap file')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    notebook_path = pathlib.Path(args.file)
    no_check_metadata = args.no_check_metadata
    no_correct_ortografic_errors = args.no_correct_ortografic_errors
    no_translate = args.no_translate
    no_convert_to_html = args.no_convert_to_html
    no_add_to_json = args.no_add_to_json
    no_add_to_sitemap = args.no_add_to_sitemap

    # Get metadata from notebook
    notebook_metadata = get_notebook_metadata(notebook_path)

    # Check if metadata is ok
    if not no_check_metadata:
        if check_if_notebook_metadata_is_ok(notebook_metadata):
            print("Metadata is ok")
        else:
            print("Metadata is not ok")
            exit(1)
    
    # Correct ortographic errors
    if not no_correct_ortografic_errors:
        if ask_for_something("\nDo you want correct ortographic errors? (y/n)", ['y', 'yes'], ['n', 'no']):
            # Get corrections from gemini and save them in a json if there aren't corrections json file
            ortografic_corrections_jupyter_notebook(notebook_path)

    # Translate notebook
    if not no_translate:
        if ask_for_something("\nDo you want to translate the notebook? (y/n)", ['y', 'yes'], ['n', 'no']):
            # Translate notebook
            translate_jupyter_notebook(notebook_path)
    
    # Convert to HTML
    if not no_convert_to_html:
        if ask_for_something("\nDo you want to convert the notebook to html? (y/n)", ['y', 'yes'], ['n', 'no']):
            print("\nConverting to HTML")
            notebook_title = notebook_metadata[3]
            convert_to_html(notebook_path, notebook_metadata, notebook_title)

    # Add to json
    if not no_add_to_json:
        if ask_for_something("\nDo you want to add the astro metadata to the json file? (y/n)", ['y', 'yes'], ['n', 'no']):
            add_page_to_its_json_file_from_metadata(notebook_metadata, notebook_path)

    # Add to sitemap
    if not no_add_to_sitemap:
        if ask_for_something("\nDo you want to add the astro metadata to the sitemap file? (y/n)", ['y', 'yes'], ['n', 'no']):
            add_page_to_its_sitemap_from_metadata(notebook_metadata, notebook_path)