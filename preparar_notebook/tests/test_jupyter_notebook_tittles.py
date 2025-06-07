import unittest
import json
import os
import sys

# Add the src directory to sys.path to allow importing jupyter_notebook_tittles
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from jupyter_notebook_tittles import extract_titles

class TestExtractTitles(unittest.TestCase):

    def setUp(self):
        # Create dummy notebook files for testing
        self.test_dir = os.path.dirname(__file__)
        self.notebook_with_titles_path = os.path.join(self.test_dir, 'test_notebook_with_titles.ipynb')
        self.notebook_no_titles_path = os.path.join(self.test_dir, 'test_notebook_no_titles.ipynb')
        self.notebook_empty_cells_path = os.path.join(self.test_dir, 'test_notebook_empty_cells.ipynb')
        self.notebook_malformed_json_path = os.path.join(self.test_dir, 'test_notebook_malformed.ipynb')

        # Notebook with various titles
        notebook_content_with_titles = {
            "cells": [
                {"cell_type": "markdown", "source": ["# Title H1"]},
                {"cell_type": "code", "source": ["print('hello')"]},
                {"cell_type": "markdown", "source": ["## Title H2"]},
                {"cell_type": "markdown", "source": ["### Title H3 with spaces  "]},
                {"cell_type": "markdown", "source": ["    #### Indented H4"]},
                {"cell_type": "markdown", "source": ["##### Title H5\nMore text"]},
                {"cell_type": "markdown", "source": ["###### Title H6"]},
                {"cell_type": "markdown", "source": ["Not a title"]},
                {"cell_type": "markdown", "source": ["#Another H1 but no space"]}, # Should not be matched
                {"cell_type": "markdown", "source": ["# Valid H1\n## Also Valid H2 in same cell"]}
            ],
            "nbformat": 4, "nbformat_minor": 2
        }
        with open(self.notebook_with_titles_path, 'w') as f:
            json.dump(notebook_content_with_titles, f)

        # Notebook with no titles
        notebook_content_no_titles = {
            "cells": [
                {"cell_type": "markdown", "source": ["Just some text."]},
                {"cell_type": "code", "source": ["a = 1"]},
                {"cell_type": "markdown", "source": ["Another paragraph."]}
            ],
            "nbformat": 4, "nbformat_minor": 2
        }
        with open(self.notebook_no_titles_path, 'w') as f:
            json.dump(notebook_content_no_titles, f)

        # Notebook with empty or no source in markdown cells
        notebook_content_empty_cells = {
            "cells": [
                {"cell_type": "markdown", "source": []},
                {"cell_type": "markdown", "source": None}, # Source might be None
                {"cell_type": "markdown", "metadata": {}, "source": ["# A title here"]},
                {"cell_type": "markdown"} # Cell with no source key
            ],
            "nbformat": 4, "nbformat_minor": 2
        }
        with open(self.notebook_empty_cells_path, 'w') as f:
            json.dump(notebook_content_empty_cells, f)

        # Malformed JSON file
        with open(self.notebook_malformed_json_path, 'w') as f:
            f.write("this is not valid json")

    def tearDown(self):
        # Clean up dummy files
        os.remove(self.notebook_with_titles_path)
        os.remove(self.notebook_no_titles_path)
        os.remove(self.notebook_empty_cells_path)
        os.remove(self.notebook_malformed_json_path)
        # Remove dummy_notebook.ipynb from src if it exists from previous step
        src_dummy_notebook = os.path.join(self.test_dir, '../src/dummy_notebook.ipynb')
        if os.path.exists(src_dummy_notebook):
            os.remove(src_dummy_notebook)


    def test_notebook_with_various_titles(self):
        expected_titles = [
            {'text': 'Title H1', 'level': 'h1'},
            {'text': 'Title H2', 'level': 'h2'},
            {'text': 'Title H3 with spaces', 'level': 'h3'},
            {'text': 'Indented H4', 'level': 'h4'},
            {'text': 'Title H5', 'level': 'h5'},
            {'text': 'Title H6', 'level': 'h6'},
            {'text': 'Valid H1', 'level': 'h1'},
            {'text': 'Also Valid H2 in same cell', 'level': 'h2'}
        ]
        titles = extract_titles(self.notebook_with_titles_path)
        self.assertEqual(titles, expected_titles)

    def test_notebook_with_no_titles(self):
        titles = extract_titles(self.notebook_no_titles_path)
        self.assertEqual(titles, [])

    def test_non_existent_notebook(self):
        # Redirect stdout to check print message for error
        # For now, just check if it returns an empty list as per current implementation
        titles = extract_titles("non_existent_notebook.ipynb")
        self.assertEqual(titles, [])
        # Add assertion for printed error message if possible, or ensure logging in actual function

    def test_notebook_with_empty_and_missing_source_cells(self):
        expected_titles = [{'text': 'A title here', 'level': 'h1'}]
        titles = extract_titles(self.notebook_empty_cells_path)
        self.assertEqual(titles, expected_titles)

    def test_malformed_json_notebook(self):
        titles = extract_titles(self.notebook_malformed_json_path)
        self.assertEqual(titles, [])

if __name__ == '__main__':
    unittest.main()
