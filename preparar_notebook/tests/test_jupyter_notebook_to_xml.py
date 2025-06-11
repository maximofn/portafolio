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

        # Open 2024-09-09-Tuplas-de-un-solo-elemento.ipynb and copy the content to the src directory
        self.test_dir = Path(__file__).parent
        with open(os.path.join(self.test_dir, '2024-09-09-Tuplas-de-un-solo-elemento.ipynb'), 'r') as f:
            notebook_content = json.load(f)
        with open(os.path.join(self.test_dir, '../src/2024-09-09-Tuplas-de-un-solo-elemento.ipynb'), 'w') as f:
            json.dump(notebook_content, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        os.remove(os.path.join(self.test_dir, '../src/2024-09-09-Tuplas-de-un-solo-elemento.ipynb'))

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
    
    def test_convert_notebook_to_xml_with_2024_09_09_Tuplas_de_un_solo_elemento(self):
        xml_file = convert_notebook_to_xml(os.path.join(self.test_dir, '../src/2024-09-09-Tuplas-de-un-solo-elemento.ipynb'))
        self.assertTrue(xml_file.exists())
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_file)
        root = tree.getroot()
        tags = [child.tag for child in root]
        expected_tags = ['markdown', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown']
        self.assertEqual(tags, expected_tags)
        self.assertEqual(root.find('markdown').text, '# Tuplas de un solo elemento')
        self.assertEqual(root.find('input_code').text, "list = [1]\ntype(list)")
        self.assertEqual(root.find('output_code').text, 'list')
        os.remove(xml_file)

if __name__ == '__main__':
    unittest.main()
