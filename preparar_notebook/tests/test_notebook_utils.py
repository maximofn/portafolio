from unittest.mock import patch
import unittest
import sys
import os

# Add the src directory to the path so we can import notebook_utils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from notebook_utils import Notebook

class Test_notebook_utils(unittest.TestCase):
    def setUp(self):
        # Use a notebook file that actually exists in the tests directory
        test_notebook_path = os.path.join(os.path.dirname(__file__), "2024-09-09-Tuplas-de-un-solo-elemento.ipynb")
        self.notebook = Notebook(test_notebook_path)
    
    def test_get_content_as_json(self):
        content = self.notebook.get_content_as_json()
        self.assertIsNotNone(content)
    
    def test_cells(self):
        cells = self.notebook.cells()
        self.assertIsInstance(cells, list)

    def test_number_cells(self):
        number_cells = self.notebook.number_cells()
        self.assertEqual(number_cells, 14)

    def test_markdown_cells(self):
        markdown_cells = self.notebook.markdown_cells()
        self.assertIsInstance(markdown_cells, list)

    def test_number_markdown_cells(self):
        number_markdown_cells = self.notebook.number_markdown_cells()
        self.assertEqual(number_markdown_cells, 8)
