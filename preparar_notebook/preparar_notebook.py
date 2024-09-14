import argparse
import pathlib
from get_notebook_metadata import get_notebook_metadata, check_if_notebook_metadata_is_ok

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
        print("Metadata is ok")
    else:
        print("Metadata is not ok")
        exit(1)