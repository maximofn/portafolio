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
        
        # Open test_get_notebook_metadata.ipynb and copy the content to the src directory
        with open(os.path.join(self.test_dir, 'test_get_notebook_metadata.ipynb'), 'r') as f:
            notebook_content = json.load(f)
        with open(os.path.join(self.test_dir, '../src/test_get_notebook_metadata.ipynb'), 'w') as f:
            json.dump(notebook_content, f)

    def tearDown(self):
        # Clean up dummy files
        os.remove(self.notebook_with_titles_path)
        os.remove(self.notebook_no_titles_path)
        os.remove(self.notebook_empty_cells_path)
        os.remove(self.notebook_malformed_json_path)
        os.remove(os.path.join(self.test_dir, '../src/test_get_notebook_metadata.ipynb'))
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
    
    def test_python_notebook(self):
        expected_titles = [{'text': 'Introducción a Python', 'level': 'h1'}, {'text': '1. Resumen', 'level': 'h2'}, {'text': '2. Tipos de datos de Python', 'level': 'h2'}, {'text': '2.1. Strings', 'level': 'h3'}, {'text': '2.2. Números', 'level': 'h3'}, {'text': '2.2.1. Enteros', 'level': 'h4'}, {'text': '2.2.2. Float', 'level': 'h4'}, {'text': '2.2.3. Complejos', 'level': 'h4'}, {'text': '2.2.4. Conversión', 'level': 'h4'}, {'text': '2.3. Secuencias', 'level': 'h3'}, {'text': '2.3.1. Listas', 'level': 'h4'}, {'text': '2.3.1.1. Editar listas', 'level': 'h5'}, {'text': '2.3.1.2. List comprehension', 'level': 'h5'}, {'text': '2.3.1.3. Ordenar listas', 'level': 'h5'}, {'text': '2.3.1.4. Copiar listas', 'level': 'h5'}, {'text': '2.3.1.5. Concatenar listas', 'level': 'h5'}, {'text': '2.3.2. Tuplas', 'level': 'h4'}, {'text': '2.3.2.1. Modificar tuplas', 'level': 'h5'}, {'text': '2.3.2.2. Desempaquetar tuplas', 'level': 'h5'}, {'text': '2.3.2.3. Concatenar tuplas', 'level': 'h5'}, {'text': '2.3.2.4. Métodos de las tuplas', 'level': 'h5'}, {'text': '2.3.3. Range', 'level': 'h4'}, {'text': '2.4. Diccionarios', 'level': 'h3'}, {'text': '2.4.1. Acceder a los ítems', 'level': 'h4'}, {'text': '2.4.2. Modificar los ítems', 'level': 'h4'}, {'text': '2.4.3. Añadir ítems', 'level': 'h4'}, {'text': '2.4.4. Eliminar items', 'level': 'h4'}, {'text': '2.4.5. Copiar diccionarios', 'level': 'h4'}, {'text': '2.4.6. Diccionarios anidados', 'level': 'h4'}, {'text': '2.4.7. Métodos de los diccionarios', 'level': 'h4'}, {'text': '2.4.8. Dictionary comprehension', 'level': 'h4'}, {'text': '2.5. Sets', 'level': 'h3'}, {'text': '2.5.1. Set', 'level': 'h4'}, {'text': '2.5.1.1. Añadir ítems', 'level': 'h5'}, {'text': '2.5.1.2. Eliminar ítems', 'level': 'h5'}, {'text': '2.5.1.3. Unir ítems', 'level': 'h5'}, {'text': '2.5.1.4. Métodos de los sets', 'level': 'h5'}, {'text': '2.5.2. Frozenset', 'level': 'h4'}, {'text': '2.6. Booleanos', 'level': 'h3'}, {'text': '2.6.1. Otros tipos de datos True o False', 'level': 'h4'}, {'text': '2.7. Binarios', 'level': 'h3'}, {'text': '2.7.1. Bytes', 'level': 'h4'}, {'text': '2.7.2. Bytearray', 'level': 'h4'}, {'text': '2.7.3. Memoryview', 'level': 'h4'}, {'text': '3. Operadores', 'level': 'h2'}, {'text': '3.1. Operadores aritméticos', 'level': 'h3'}, {'text': '3.2. Operadores de comparación', 'level': 'h3'}, {'text': '3.3. Operadores lógicos', 'level': 'h3'}, {'text': '3.4. Operadores de identidad', 'level': 'h3'}, {'text': '3.5. Operadores de pertenencia', 'level': 'h3'}, {'text': '3.6. Operadores bit a bit', 'level': 'h3'}, {'text': '3.7. Operadores de asignación', 'level': 'h3'}, {'text': '4. Control de flujo', 'level': 'h2'}, {'text': '4.1. If', 'level': 'h3'}, {'text': '4.2. While', 'level': 'h3'}, {'text': '4.3. For', 'level': 'h3'}, {'text': '5. Funciones', 'level': 'h2'}, {'text': '5.1. Built in functions', 'level': 'h3'}, {'text': '5.2. Documentación de una función', 'level': 'h3'}, {'text': '5.3. Decoradores', 'level': 'h3'}, {'text': '5.4. `*args` y `**kwargs`', 'level': 'h3'}, {'text': 'código de la función aquí', 'level': 'h1'}, {'text': '5.4.1. `*args`', 'level': 'h4'}, {'text': '5.4.2. `**kwargs`', 'level': 'h4'}, {'text': '6. Funciones adicionales', 'level': 'h2'}, {'text': '6.1. Funciones *lambda*', 'level': 'h3'}, {'text': '6.2. Función `map`', 'level': 'h3'}, {'text': '6.3. Función `filter`', 'level': 'h3'}, {'text': '6.4. Función `reduce`', 'level': 'h3'}, {'text': '6.5. Función `zip`', 'level': 'h3'}, {'text': '6.5. Generadores', 'level': 'h3'}, {'text': '6.6. High order functions', 'level': 'h3'}, {'text': '7. Clases y objetos', 'level': 'h2'}, {'text': '7.1. Herencia', 'level': 'h3'}, {'text': '7.2. Sobrecarga de operadores', 'level': 'h3'}, {'text': '7.3. Iteradores personalizados', 'level': 'h3'}, {'text': '7.4. Llamada a objetos como funciones', 'level': 'h3'}, {'text': '7.5. Atributos y funciones privados', 'level': 'h3'}, {'text': '8. Iteradores', 'level': 'h2'}, {'text': '8.1. Crear un objeto iterador', 'level': 'h3'}, {'text': '8.2. Iterar obteniendo el índice y el valor', 'level': 'h3'}, {'text': '8.3. Iterar por dos objetos iterables a la vez', 'level': 'h3'}, {'text': '9. Alcance de variables', 'level': 'h2'}, {'text': '9.1. Alcance local', 'level': 'h3'}, {'text': '9.2. Alcance global', 'level': 'h3'}, {'text': '10. Módulos', 'level': 'h2'}, {'text': '10.1. Entry points: archivos como módulos y no como scripts', 'level': 'h3'}, {'text': '11. Paquetes', 'level': 'h2'}, {'text': '12. Try... Except', 'level': 'h2'}, {'text': '12.1. Crear una excepción', 'level': 'h3'}, {'text': '13. Keywords o palabras reservadas', 'level': 'h2'}, {'text': '14. El Zen de Python', 'level': 'h2'}]
        titles = extract_titles(os.path.join(self.test_dir, '../src/test_get_notebook_metadata.ipynb'))
        self.assertEqual(titles, expected_titles)

if __name__ == '__main__':
    unittest.main()
