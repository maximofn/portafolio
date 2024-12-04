from unittest.mock import patch
import unittest
from preparar_notebook.src.format_code_blocks import remove_empty_lines, format_code_blocks

class Test_format_code_blocks(unittest.TestCase):
    def test_remove_empty_lines_with_empty_lines(self):
        lines = [
            "",
            "></CodeBlockOutputCell>",
            "",
            "",
            "",
            "",
            "",
            "end"]
        lines_without_empty_lines = [
            '',
            '></CodeBlockOutputCell>',
            'end'
        ]
        lines, lines_removed = remove_empty_lines(lines)
        self.assertEqual(lines, lines_without_empty_lines)
        self.assertTrue(lines_removed)
    
    def test_remove_empty_lines_without_empty_lines(self):
        lines = [
            '></CodeBlockOutputCell>',
            'end'
        ]
        lines_without_empty_lines, lines_removed = remove_empty_lines(lines)
        self.assertEqual(lines_without_empty_lines, lines)
        self.assertFalse(lines_removed)
    
    @unittest.skip('Not implemented yet')
    def test_format_code_blocks(self):
        pass