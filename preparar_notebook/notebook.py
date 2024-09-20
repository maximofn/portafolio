import json

class Notebook:
    def __init__(self, path, end_name=None):
        self.path = path
        self.content = None
        if end_name:
            self.path = self.path.parent / f"{self.path.stem}_{end_name}{self.path.suffix}"

    def get_content_as_json(self):
        with open(self.path, 'r') as f:
            return json.load(f)
    
    def cells(self):
        content = self.get_content_as_json()
        return content['cells']
    
    def number_cells(self):
        return len(self.cells())
    
    def markdown_cells(self):
        return [cell for cell in self.cells() if cell['cell_type'] == 'markdown']

    def number_markdown_cells(self):
        return len(self.markdown_cells())
    
    def save_content_dict(self, content):
        with open(self.path, 'w') as file:
            json.dump(content, file, indent=2)
        
    def save_cells(self, cells):
        content = self.get_content_as_json()
        content['cells'] = cells
        self.save_content_dict(content)