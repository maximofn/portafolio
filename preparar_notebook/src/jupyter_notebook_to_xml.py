import argparse
import json
import pathlib
import re
import xml.etree.ElementTree as ET


def notebook_to_xml_tree(notebook_path):
    """Return an ElementTree representing the notebook converted to XML."""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_json = json.load(f)

    root = ET.Element('notebook')

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    for cell in notebook_json.get('cells', []):
        cell_type = cell.get('cell_type')
        if cell_type == 'markdown':
            md = ''.join(cell.get('source', []))
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
    notebook_path = pathlib.Path(notebook_path)
    xml_tree = notebook_to_xml_tree(notebook_path)

    # Indent the XML tree for pretty printing.
    # This adds newlines and indentation to make the XML file readable.
    ET.indent(xml_tree, space="  ")

    xml_dir = notebook_path.parent / 'xml_files'
    xml_dir.mkdir(exist_ok=True)
    xml_file = xml_dir / f"{notebook_path.stem}.xml"
    xml_tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    return xml_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Jupyter notebook to XML')
    parser.add_argument('notebook_path', help='Path to the Jupyter notebook')
    args = parser.parse_args()

    convert_notebook_to_xml(args.notebook_path)
