import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from jupyter_notebook_to_xml import convert_notebook_to_xml

class TestJupyterNotebookToXml(unittest.TestCase):
    def setUp(self):
        # Create tmpdir
        self.tmpdir = Path(tempfile.mkdtemp())

        # Create notebooks_translated folder into tmpdir
        self.nb_translated_dir = self.tmpdir / 'notebooks_translated'
        self.nb_translated_dir.mkdir(exist_ok=True)

        # Create notebooks
        self.nb_path_es = self.tmpdir / 'test_notebook_es.ipynb'
        self.nb_path_en = self.nb_translated_dir / 'test_notebook_EN.ipynb'
        self.nb_path_pt = self.nb_translated_dir / 'test_notebook_PT.ipynb'
        notebook_content_es = {
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
        notebook_content_en = {
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
        notebook_content_pt = {
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
        with open(self.nb_path_es, 'w') as f:
            json.dump(notebook_content_es, f)
        with open(self.nb_path_en, 'w') as f:
            json.dump(notebook_content_en, f)
        with open(self.nb_path_pt, 'w') as f:
            json.dump(notebook_content_pt, f)

        # Open 2024-09-09-Tuplas-de-un-solo-elemento.ipynb and copy the content to the src directory
        self.test_dir = Path(__file__).parent
        with open(os.path.join(self.test_dir, '2024-09-09-Tuplas-de-un-solo-elemento.ipynb'), 'r') as f:
            notebook_content = json.load(f)
        with open(os.path.join(self.test_dir, '../src/2024-09-09-Tuplas-de-un-solo-elemento.ipynb'), 'w') as f:
            json.dump(notebook_content, f)

        # Create preparar_notebook/src/translated_notebooks directory
        self.translated_notebooks_dir = self.test_dir.parent
        self.translated_notebooks_src_dir = self.translated_notebooks_dir / 'src'
        self.translated_notebooks_src_translated_notebooks_dir = self.translated_notebooks_src_dir / 'notebooks_translated'
        self.translated_notebooks_src_translated_notebooks_dir.mkdir(exist_ok=True)

        # Open 2024-09-09-Tuplas-de-un-solo-elemento_EN.ipynb and copy the content to the src directory
        with open(os.path.join(self.test_dir, '2024-09-09-Tuplas-de-un-solo-elemento_EN.ipynb'), 'r') as f:
            notebook_content_en = json.load(f)
        with open(os.path.join(self.translated_notebooks_src_translated_notebooks_dir, '2024-09-09-Tuplas-de-un-solo-elemento_EN.ipynb'), 'w') as f:
            json.dump(notebook_content_en, f)

        # Open 2024-09-09-Tuplas-de-un-solo-elemento_PT.ipynb and copy the content to the src directory
        with open(os.path.join(self.test_dir, '2024-09-09-Tuplas-de-un-solo-elemento_PT.ipynb'), 'r') as f:
            notebook_content_pt = json.load(f)
        with open(os.path.join(self.translated_notebooks_src_translated_notebooks_dir, '2024-09-09-Tuplas-de-un-solo-elemento_PT.ipynb'), 'w') as f:
            json.dump(notebook_content_pt, f)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        os.remove(os.path.join(self.test_dir, '../src/2024-09-09-Tuplas-de-un-solo-elemento.ipynb'))
        os.remove(os.path.join(self.translated_notebooks_src_translated_notebooks_dir, '2024-09-09-Tuplas-de-un-solo-elemento_EN.ipynb'))
        os.remove(os.path.join(self.translated_notebooks_src_translated_notebooks_dir, '2024-09-09-Tuplas-de-un-solo-elemento_PT.ipynb'))

    def test_convert_notebook_to_xml(self):
        xml_files = convert_notebook_to_xml(str(self.nb_path_es))
        self.assertEqual(len(xml_files), 3)
        for xml_file in xml_files:
            self.assertTrue(xml_file.exists())
            tree = ET.parse(xml_file)
            root = tree.getroot()
            tags = [child.tag for child in root]
            self.assertEqual(tags, ['markdown', 'input_code', 'output_code'])
            self.assertEqual(root.find('markdown').text, '# Title')
            self.assertEqual(root.find('input_code').text, "print('hi')")
            self.assertEqual(root.find('output_code').text, 'hi\n')
    
    def test_convert_notebook_to_xml_with_2024_09_09_Tuplas_de_un_solo_elemento(self):
        xml_files = convert_notebook_to_xml(os.path.join(self.translated_notebooks_src_dir, '2024-09-09-Tuplas-de-un-solo-elemento.ipynb'))
        self.assertEqual(len(xml_files), 3)
        for xml_file in xml_files:
            self.assertTrue(xml_file.exists())
            tree = ET.parse(xml_file)
            root = tree.getroot()
            tags = [child.tag for child in root]
            if '_EN' in xml_file.name or '_PT' in xml_file.name:
                expected_tags = ['markdown', 'markdown', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown']
            else:
                expected_tags = ['markdown', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown', 'input_code', 'output_code', 'markdown']
            self.assertEqual(tags, expected_tags)
            if '_EN' in xml_file.name:
                self.assertEqual(root.find('markdown').text, '# Single Element Tuples')
            elif '_PT' in xml_file.name:
                self.assertEqual(root.find('markdown').text, '# Tuplas de um único elemento')
            else:
                self.assertEqual(root.find('markdown').text, '# Tuplas de un solo elemento')
            self.assertEqual(root.find('input_code').text, "list = [1]\ntype(list)")
            self.assertEqual(root.find('output_code').text, 'list')
            os.remove(xml_file)
    
    def test_convert_notebook_to_xml_with_test_latex(self):
        # Paths
        notebook_path = os.path.join(self.test_dir, 'test-latex.ipynb')
        true_xml_path = os.path.join(self.test_dir, 'test-latex.xml')
        # Open xml file
        with open(true_xml_path, 'r') as f:
            expected_xml = f.read()
        # Convert notebook to xml
        xml_files = convert_notebook_to_xml(notebook_path)
        print("-"*100)
        print(f"notebook path: {notebook_path}")
        print(f"true xml path: {true_xml_path}")
        print(f"xml files: {xml_files}")
        print("-"*100)
        # Check that the xml files are equal to the test-latex.xml file
        self.assertEqual(len(xml_files), 3)
        # Iterate over xml files
        for xml_file in xml_files:
            # Check that the xml file exists
            self.assertTrue(xml_file.exists())
            # Check that the xml file is equal to the test-latex.xml file
            with open(xml_file, 'r') as f:
                actual_xml = f.read()
            print("-"*100)
            print(f"actual xml: {actual_xml}")
            print(f"expected xml: {expected_xml}")
            print("-"*100)
            self.assertEqual(actual_xml, expected_xml)
            # Remove xml file
            os.remove(xml_file)

if __name__ == '__main__':
    unittest.main()
