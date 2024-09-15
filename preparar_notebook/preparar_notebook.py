import argparse
import pathlib
from get_notebook_metadata import get_notebook_metadata, check_if_notebook_metadata_is_ok
from preprocess_jupyter_notebook import create_corrections_dict, apply_corrections
from error_codes import QUOTA_EXCEEDED_ERROR
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Preparar notebook')
    parser.add_argument('file', type=str, help='File to prepare')   # Writing `file` and not `--file` makes that the argument is positional. It's not necessary to write `--file` when calling the script
    parser.add_argument('--corrections', type=str, help='json with corrections (optional)', default=None)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    notebook_path = pathlib.Path(args.file)
    corrections_path = args.corrections

    # Get metadata from notebook
    notebook_metadata = get_notebook_metadata(notebook_path)

    # Check if metadata is ok
    if check_if_notebook_metadata_is_ok(notebook_metadata):
        print("Metadata is ok\n")
    else:
        print("Metadata is not ok")
        exit(1)
    
    # Get corrections from gemini and save them in a json
    if corrections_path is None:
        notebook_correctios_dict = create_corrections_dict(notebook_path)
    
    # Get corrections from a json
    with open(corrections_path, 'r') as archivo:
        notebook_correctios_dict = json.load(archivo)
    
    # Apply corrections
    apply_corrections(notebook_path, notebook_correctios_dict)