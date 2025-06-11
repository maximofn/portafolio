from unittest.mock import patch
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from notebook_utils import Notebook

class Test_notebook_utils(unittest.TestCase):
    def setUp(self):
        self.notebook = Notebook("posts/2021-02-11-Introduccion-a-Python.ipynb")
    
    def test_get_content_as_json(self):
        content = self.notebook.get_content_as_json()
        self.assertIsNotNone(content)
    
    def test_cells(self):
        cells = self.notebook.cells()
        self.assertIsInstance(cells, list)

    def test_number_cells(self):
        number_cells = self.notebook.number_cells()
        self.assertEqual(number_cells, 723)

    def test_markdown_cells(self):
        markdown_cells = self.notebook.markdown_cells()
        self.assertIsInstance(markdown_cells, list)

    def test_number_markdown_cells(self):
        number_markdown_cells = self.notebook.number_markdown_cells()
        self.assertEqual(number_markdown_cells, 412)
