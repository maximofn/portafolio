import json
import re


def get_notebook_tittles(notebook_path):
    with open(notebook_path, 'r') as file:
        notebook_json = json.load(file)

    tittles = []
    for cell in notebook_json.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            for line in cell.get('source', []):
                line_stripped = line.rstrip()
                match = re.match(r'^\s{0,3}(#{1,6})\s+(.*)$', line_stripped)
                if match:
                    level = f"h{len(match.group(1))}"
                    text = match.group(2).strip()
                    tittles.append({'text': text, 'level': level})
    return tittles
