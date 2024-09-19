import json

class Notebook:
    def __init__(self, path):
        self.path = path

    def get_content_as_json(self):
        with open(self.path, 'r') as f:
            return json.load(f)