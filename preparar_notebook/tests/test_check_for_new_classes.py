from unittest.mock import patch
import unittest
from preparar_notebook.src.check_for_new_classes import check_for_new_classes

class Test_check_for_new_classes(unittest.TestCase):
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_check_for_new_classes_new_class(self, mock_stdout):    # With mock_stdout we can test without printing to the console
        try:
            response = check_for_new_classes('preparar_notebook/tests/test_check_for_new_classes_new_class.astro')
            self.assertEqual(response, None)
        except SystemExit as e:
            self.assertEqual(e.code, 1)

    def test_check_for_new_classes_no_new_class(self):
        response = check_for_new_classes('preparar_notebook/tests/test_check_for_new_classes_no_new_class.astro')
        self.assertEqual(response, None)
