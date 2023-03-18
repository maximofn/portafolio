#!/usr/bin/env python3

import argparse
import re
import sys
import os

# Add path to the modules
# sys.path.append("../../jupyter-translator/")
import utils_jupyter as uj


def path_name_ext_from_file(file):
    path, name = os.path.split(file)
    name, extension = os.path.splitext(name)
    simplex_name = name[11:].replace("-", " ")
    return path, name, extension, simplex_name


def parse_arguments():
    parser = argparse.ArgumentParser(description='Jupyter markdown bas to jupyter markdown code Help')
    parser.add_argument('-f', '--file', help='The notebook to convert', required=True)
    
    args = parser.parse_args()
    if args.file:
        path, name, extension, _ = path_name_ext_from_file(args.file)
        if extension == '.ipynb':
            print(f"\tConverting {path}{name}{extension}")
        else:
            raise Exception(f"File {path}{name}{extension} is not a Jupyter notebook")
    else:
        raise Exception('No file specified')
    
    return parser.parse_args()



def main(file):
    # Open notebook and get cells and headers
    notebook = uj.open_notebook_to_read(file)  # Open the notebook as a dictionary
    if notebook is None:
        sys.exit(1)
    cells = notebook['cells']   # Get only with the cells
    for cell in cells:
        if cell['cell_type'] == 'markdown':
            if cell['source'][0].startswith('```') and cell['source'][-1].startswith('```'):
                cell['cell_type'] = 'code'
                cell['execution_count'] = 8
                input = f"!{cell['source'][1]}"
                input = input.replace("\n", "")
                outputs = cell['source'][2:-1]
                cell['source'] = [input]
                if len(outputs) > 0:
                    output_string = ""
                    for output in outputs:
                        output_string += output
                    output_string = output_string.replace("~", "~")
                    cell['outputs'] = [{'output_type': 'stream', 'name': 'stdout', 'text': output_string}]
    
    # Save notebook
    path, name, extension, simplex_name = path_name_ext_from_file(file)
    new_file = f"{path}{name}-code{extension}"
    uj.dict_to_ipynb(notebook, new_file)


if __name__ == '__main__':
    args = parse_arguments()
    main(args.file)