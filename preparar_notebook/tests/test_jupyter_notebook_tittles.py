import unittest
from preparar_notebook.src.jupyter_notebook_tittles import get_notebook_tittles


class Test_jupyter_notebook_tittles(unittest.TestCase):
    def setUp(self):
        self.notebook = "preparar_notebook/tests/test_get_notebook_metadata.ipynb"

    def test_number_of_tittles(self):
        tittles = get_notebook_tittles(self.notebook)
        self.assertEqual(len(tittles), 91)

    def test_some_tittles(self):
        tittles = get_notebook_tittles(self.notebook)
        self.assertEqual(tittles[0], {"text": "Introducción a Python", "level": "h1"})
        self.assertEqual(tittles[1], {"text": "1. Resumen", "level": "h2"})
        self.assertEqual(tittles[2], {"text": "2. Tipos de datos de Python", "level": "h2"})
        self.assertEqual(tittles[3], {"text": "2.1. Strings", "level": "h3"})
        self.assertEqual(tittles[-1], {"text": "14. El Zen de Python", "level": "h2"})
