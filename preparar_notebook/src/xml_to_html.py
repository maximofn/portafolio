import xml.etree.ElementTree as ET
import argparse
from generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns

def process_xml_file(xml_file_path):
    """
    Parses an XML file, and for markdown cells, processes their content.

    Args:
        xml_file_path (str): The path to the input XML file.

    Returns:
        None: This function prints directly and doesn't return significant content.
              It might return error messages as strings in case of file issues.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except FileNotFoundError:
        print("Error: XML file not found.")
        return "Error: XML file not found."
    except ET.ParseError:
        print("Error: Could not parse XML file.")
        return "Error: Could not parse XML file."

    if root.tag == "notebook":
        for cell in root.findall('cell'):
            cell_type = cell.get('type')
            if cell_type == 'markdown':
                cell_content = cell.text or ""
                print(f"--- Processing Markdown Cell ---")
                markdown_list = generic_markdown_to_list_specific_markdowns(cell_content.strip())
                print(markdown_list)
                print(f"--- End of Markdown Cell ---")
    else:
        print(f"XML root tag is '{root.tag}', not 'notebook'. No cells processed.")
        return f"XML root tag is '{root.tag}', not 'notebook'. No cells processed."

    return "Processing complete."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process an XML notebook file and handle markdown cells.")
    parser.add_argument("xml_file", help="The path to the input XML file.")
    args = parser.parse_args()

    result = process_xml_file(args.xml_file)
    if result:
        print(result)
