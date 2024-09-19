import argparse
import pathlib
from get_notebook_metadata import get_notebook_metadata, check_if_notebook_metadata_is_ok, get_portafolio_path
from corrections_jupyter_notebook import ortografic_corrections_jupyter_notebook
from error_codes import QUOTA_EXCEEDED_ERROR
import json
from utils import ask_for_something

def parse_args():
    parser = argparse.ArgumentParser(description='Preparar notebook')
    parser.add_argument('file', type=str, help='File to prepare')   # Writing `file` and not `--file` makes that the argument is positional. It's not necessary to write `--file` when calling the script
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    notebook_path = pathlib.Path(args.file)

    # Get metadata from notebook
    notebook_metadata = get_notebook_metadata(notebook_path)

    # Check if metadata is ok
    if check_if_notebook_metadata_is_ok(notebook_metadata):
        print("Metadata is ok\n")
    else:
        print("Metadata is not ok")
        exit(1)
    
    # Correct ortographic errors
    if ask_for_something("Do you want correct ortographic errors? (y/n)", ['y', 'yes'], ['n', 'no']):
        # Get corrections from gemini and save them in a json if there aren't corrections json file
        ortografic_corrections_jupyter_notebook(notebook_path)

    # Translate notebook
    if ask_for_something("Do you want to translate the notebook? (y/n)", ['y', 'yes'], ['n', 'no']):
        # Translate notebook
        pass