import argparse
import pathlib
from get_notebook_metadata import get_notebook_metadata, check_if_notebook_metadata_is_ok
from preprocess_jupyter_notebook import correct_notebook
from error_codes import QUOTA_EXCEEDED_ERROR

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
    
    # Corrections from gemini
    notebook_correctios_dict = correct_notebook(notebook_path)
    if notebook_correctios_dict and notebook_correctios_dict != QUOTA_EXCEEDED_ERROR:
        print("Notebook corrections:")
        print(notebook_correctios_dict)
    elif notebook_correctios_dict == QUOTA_EXCEEDED_ERROR:
        print("Quota exceeded error")