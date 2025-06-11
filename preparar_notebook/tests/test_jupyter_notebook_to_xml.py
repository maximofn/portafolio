import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from jupyter_notebook_to_xml import convert_notebook_to_xml

class TestJupyterNotebookToXml(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.nb_path = self.tmpdir / 'test_notebook.ipynb'
        notebook_content = {
            "cells": [
                {"cell_type": "markdown", "source": ["# Title"]},
                {
                    "cell_type": "code",
                    "source": ["print('hi')"],
                    "outputs": [
                        {"output_type": "stream", "name": "stdout", "text": ["hi\n"]}
                    ]
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 2
        }
        with open(self.nb_path, 'w') as f:
            json.dump(notebook_content, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_convert_notebook_to_xml(self):
        xml_file = convert_notebook_to_xml(str(self.nb_path))
        self.assertTrue(xml_file.exists())
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tags = [child.tag for child in root]
        self.assertEqual(tags, ['markdown', 'input_code', 'output_code'])
        self.assertEqual(root.find('markdown').text, '# Title')
        self.assertEqual(root.find('input_code').text, "print('hi')")
        self.assertEqual(root.find('output_code').text, 'hi\n')

if __name__ == '__main__':
    unittest.main()
