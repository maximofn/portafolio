from unittest.mock import patch
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from get_notebook_metadata import get_image_width_height, get_image_extension, get_notebook_metadata

class Test_get_notebook_metadata(unittest.TestCase):
    def test_get_image_width_height(self):
        width, height = get_image_width_height('https://images.maximofn.com/GPTQ-thumbnail.webp')
        self.assertEqual(width, 1024)
        self.assertEqual(height, 1024)

    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_get_image_width_height_invalid_url(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            get_image_width_height('https://images.maximofn.com/brrrrrr.webp')
        self.assertEqual(cm.exception.code, 1)
    
    def test_get_image_extension(self):
        extension = get_image_extension('https://images.maximofn.com/GPTQ-thumbnail.webp')
        self.assertEqual(extension, 'webp')

    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_get_image_extension_invalid_path(self, mock_stdout):
        with self.assertRaises(SystemExit) as cm:
            get_image_extension('tests/test_get_notebook_metadata_invalid_path,txt')
        self.assertEqual(cm.exception.code, 1)

    def test_get_notebook_metadata(self):
        notebook = "tests/test_get_notebook_metadata.ipynb"
        title_es, title_en, title_pt, end_url, description_es, description_en, description_pt, \
        keywords_es, keywords_en, keywords_pt, image, image_hover_path, witdh, height, image_extension, date = get_notebook_metadata(notebook)
        self.assertEqual(title_es, "Introducción a Python")
        self.assertEqual(title_en, "Introduction to Python")
        self.assertEqual(title_pt, "Introdução ao Python")
        self.assertEqual(end_url, "python")
        self.assertEqual(description_es, "Python 🐍 es uno de los lenguajes de programación 💻 MÁS USADO. Entra y aprende todo lo que necesitas sobre Python 🐍")
        self.assertEqual(description_en, "Python 🐍 is one of the most used programming languages 💻. Enter and learn everything you need about Python 🐍")
        self.assertEqual(description_pt, "Python 🐍 é uma das linguagens de programação 💻 MAIS USADAS. Entre e aprenda tudo o que precisa sobre Python 🐍")
        self.assertEqual(keywords_es, "python, introducción, tutorial, básico, principiantes")
        self.assertEqual(keywords_en, "python, introduction, tutorial, basic, beginners")
        self.assertEqual(keywords_pt, "python, introdução, tutorial, básico, iniciantes")
        self.assertEqual(image, "https://images.maximofn.com/icon-python.webp")
        self.assertEqual(image_hover_path, "https://images.maximofn.com/icon-python.webp")
        self.assertEqual(witdh, 800)
        self.assertEqual(height, 336)
        self.assertEqual(image_extension, "webp")
        self.assertEqual(date, "2021-02-11")
    
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_get_notebook_metadata_no_description_es(self, mock_stdout):
        notebook = "tests/test_get_notebook_metadata_no_description_es.ipynb"
        title_es, title_en, title_pt, end_url, description_es, description_en, description_pt, \
        keywords_es, keywords_en, keywords_pt, image, image_hover_path, witdh, height, image_extension, date = get_notebook_metadata(notebook)
        self.assertEqual(title_es, None)
        self.assertEqual(title_en, None)
        self.assertEqual(title_pt, None)
        self.assertEqual(end_url, None)
        self.assertEqual(description_es, None)
        self.assertEqual(description_en, None)
        self.assertEqual(description_pt, None)
        self.assertEqual(keywords_es, None)
        self.assertEqual(keywords_en, None)
        self.assertEqual(keywords_pt, None)
        self.assertEqual(image, None)
        self.assertEqual(image_hover_path, None)
        self.assertEqual(witdh, None)
        self.assertEqual(height, None)
        self.assertEqual(image_extension, None)
        self.assertEqual(date, None)
