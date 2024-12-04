import json
import copy

class Notebook:
    def __init__(self, path, add_path=None, end_name=None):
        self.path = path
        self.content = None
        if add_path:
            self.path = self.path.parent / f"{add_path}" / f"{self.path.stem}{self.path.suffix}"
        if end_name:
            self.path = self.path.parent / f"{self.path.stem}_{end_name}{self.path.suffix}"

    def get_content_as_json(self):
        if self.content:
            return self.content
        else:
            with open(self.path, 'r') as f:
                self.content = json.load(f)
                return self.content
    
    def cells(self):
        content = self.get_content_as_json()
        return content['cells']
    
    def copy_from(self, notebook):
        self.content = copy.deepcopy(notebook.content.copy())
    
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