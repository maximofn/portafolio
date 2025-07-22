import argparse
import json
import pathlib
import re
import xml.etree.ElementTree as ET

SPANISH = "ES"
ENGLISH = "EN"
PORTUGUESE = "PT"
LANGUAGES = [SPANISH, ENGLISH, PORTUGUESE]
LANGUAJES_DICT = {SPANISH: "spanish", ENGLISH: "english", PORTUGUESE: "portuguese"}

NOTEBOOKS_TRANSLATED = "notebooks_translated"

def notebook_to_xml_tree(notebook_path):
    """Return an ElementTree representing the notebook converted to XML."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_json = json.load(f)

    root = ET.Element('notebook')

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    for cell in notebook_json.get('cells', []):
        cell_type = cell.get('cell_type')
        if cell_type == 'markdown':
            if 'EN' in str(notebook_path) or 'PT' in str(notebook_path):
                num_sourece_elements = len(cell.get('source', []))
                for i,source in enumerate(cell.get('source', [])):
                    # if is the last element, do nothing
                    if i == num_sourece_elements - 1:
                        continue
                    # if the element ends with a break line, do nothing
                    if source.endswith('\n'):
                        continue
                    # else, add a break line
                    cell.get('source', []).insert(i+1, '\n')

            md = ''.join(cell.get('source', []))
            # Duplicate backslashes followed by pipe characters for LaTeX compatibility
            md = md.replace('\\|', '||')
            # Fix code blocks that have extra newline before closing backticks
            # Pattern: any character followed by three backticks and newline at the end
            md = re.sub(r'(.)```\n', r'\1\n```', md)
            elem = ET.SubElement(root, 'markdown')
            elem.text = md
        elif cell_type == 'code':
            input_code = ''.join(cell.get('source', []))
            input_elem = ET.SubElement(root, 'input_code')
            input_elem.text = input_code
            for output in cell.get('outputs', []):
                output_text = ''
                if isinstance(output, dict):
                    if 'text' in output:
                        value = output['text']
                        if isinstance(value, list):
                            output_text = ''.join(value)
                        else:
                            output_text = str(value)
                    elif 'data' in output:
                        data = output['data']
                        if isinstance(data, dict):
                            if 'text/plain' in data:
                                value = data['text/plain']
                                if isinstance(value, list):
                                    output_text = ''.join(value)
                                else:
                                    output_text = str(value)
                            else:
                                output_text = json.dumps(data)
                        else:
                            output_text = str(data)
                    elif 'name' in output and 'text' in output:
                        value = output['text']
                        if isinstance(value, list):
                            output_text = ''.join(value)
                        else:
                            output_text = str(value)
                    elif 'traceback' in output:
                        tb = output['traceback']
                        if isinstance(tb, list):
                            raw_traceback = ''.join(tb)
                            output_text = ansi_escape.sub('', raw_traceback)
                        else:
                            output_text = str(tb)
                    else:
                        output_text = str(output)
                else:
                    output_text = str(output)
                out_elem = ET.SubElement(root, 'output_code')
                out_elem.text = output_text
    return ET.ElementTree(root)


def convert_notebook_to_xml(notebook_path):
    """Convert a Jupyter notebook to XML and save it in xml_files folder."""
    # Get notebook path
    notebook_path = pathlib.Path(notebook_path)
    path = notebook_path.parent
    notebook_name = notebook_path.stem
    notebook_extension = notebook_path.suffix

    # Create the paths for the translated notebooks
    notebook_name_en = notebook_name.replace("_es", "") + "_" + ENGLISH + notebook_extension
    notebook_name_pt = notebook_name.replace("_es", "") + "_" + PORTUGUESE + notebook_extension
    notebook_paths = [notebook_path, path/NOTEBOOKS_TRANSLATED/notebook_name_en, path/NOTEBOOKS_TRANSLATED/notebook_name_pt]

    # Convert every notebook to XML
    xml_files = []
    for notebook_path in notebook_paths:
        # Convert the notebook to XML
        xml_tree = notebook_to_xml_tree(notebook_path)

        # Indent the XML tree for pretty printing.
        # This adds newlines and indentation to make the XML file readable.
        ET.indent(xml_tree, space="  ")

        # Create the xml_files folder if it doesn't exist
        xml_dir = path / 'xml_files'
        xml_dir.mkdir(exist_ok=True)

        # Create the xml file
        xml_file = xml_dir / f"{notebook_path.stem}.xml"

        # Save the xml file
        xml_tree.write(xml_file, encoding='utf-8', xml_declaration=True)

        # Add the xml file to the list
        xml_files.append(xml_file)
    
    return xml_files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Jupyter notebook to XML')
    parser.add_argument('notebook_path', help='Path to the Jupyter notebook')
    args = parser.parse_args()

    convert_notebook_to_xml(args.notebook_path)
