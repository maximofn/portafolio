import json
import xml.etree.ElementTree as ET
import sys
import argparse
import os

def convert_notebook_to_xml(notebook_path):
    """
    Converts a Jupyter notebook to XML format.
    The XML file will be saved in a subdirectory named 'xml_files'
    in the same directory as the input notebook.

    Args:
        notebook_path (str): The path to the Jupyter notebook file.
    """
    try:
        notebook_dir = os.path.dirname(os.path.abspath(notebook_path))
        notebook_filename = os.path.basename(notebook_path)
        notebook_name_without_ext = os.path.splitext(notebook_filename)[0]

        xml_dir = os.path.join(notebook_dir, "xml_files")
        if not os.path.exists(xml_dir):
            try:
                os.makedirs(xml_dir)
                print(f"Created directory: {xml_dir}")
            except OSError as e:
                print(f"Error: Could not create directory {xml_dir}. {e}")
                return

        xml_filename = f"{notebook_name_without_ext}.xml"
        xml_path = os.path.join(xml_dir, xml_filename)

    except Exception as e:
        print(f"Error processing paths: {e}")
        return

    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
    except FileNotFoundError:
        print(f"Error: Notebook file not found at {notebook_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in notebook file {notebook_path}")
        return

    root = ET.Element("notebook")

    for cell in notebook_content.get("cells", []):
        cell_type = cell.get("cell_type")
        source_list = cell.get("source", [])
        source = "".join(source_list)

        if cell_type == "markdown":
            markdown_element = ET.SubElement(root, "markdown")
            markdown_element.text = source
        elif cell_type == "code":
            input_code_element = ET.SubElement(root, "input_code")
            input_code_element.text = source

            for output in cell.get("outputs", []):
                output_text_content = ""
                output_type = output.get("output_type")

                if output_type == "stream":
                    text_data = output.get("text", [])
                    if isinstance(text_data, list):
                        output_text_content = "".join(text_data)
                    elif isinstance(text_data, str):
                        output_text_content = text_data
                elif output_type in ["execute_result", "display_data"]:
                    text_data = output.get("data", {}).get("text/plain", [])
                    if isinstance(text_data, list):
                        output_text_content = "".join(text_data)
                    elif isinstance(text_data, str):
                        output_text_content = text_data

                # Ensure newline characters are preserved if source is a list of lines
                # and also handle cases where text_data might already be a pre-joined string.
                if isinstance(source_list, list) and '\n' not in output_text_content and len(source_list) > 0 :
                    # This check is a bit heuristic. If text_data was a list of lines, "".join would keep newlines if they were there.
                    # If it was a single string from text/plain, it might or might not have newlines.
                    # The primary goal is to join list of strings with newlines if text_data itself was a list of strings.
                    # The current join "".join(text_data) above handles this.
                    # This part might need refinement based on more diverse notebook examples.
                    pass


                output_code_element = ET.SubElement(root, "output_code")
                output_code_element.text = output_text_content.strip('\n') # Strip trailing newlines from output
        # Other cell types are ignored

    tree = ET.ElementTree(root)
    try:
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)
        print(f"Notebook converted successfully to {xml_path}")
    except IOError:
        print(f"Error: Could not write XML file to {xml_path}")
    except Exception as e:
        print(f"An unexpected error occurred during XML writing: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a Jupyter notebook to XML format.")
    parser.add_argument("notebook_path", help="The path to the Jupyter notebook file (.ipynb).")

    args = parser.parse_args()

    convert_notebook_to_xml(args.notebook_path)
