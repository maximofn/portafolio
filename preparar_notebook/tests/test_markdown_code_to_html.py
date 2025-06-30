import os
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.markdown_to_html.markdown_code_to_html_converter import markdown_code_to_html

class TestMarkdownCodeToHtml(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello_world_without_space(self):
        markdown_content = "```python\nprint('hello world')\n```"
        html = markdown_code_to_html(markdown_content)
        self.assertEqual(html, '<pre><code>print(&#39;hello world&#39;)\n</code></pre>\n')

    def test_hello_world_with_space(self):
        markdown_content = "``` python\nprint('hello world')\n```"
        html = markdown_code_to_html(markdown_content)
        self.assertEqual(html, '<pre><code>print(&#39;hello world&#39;)\n</code></pre>\n')

if __name__ == '__main__':
    unittest.main()
