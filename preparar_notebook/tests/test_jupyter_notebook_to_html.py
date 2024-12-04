from unittest.mock import patch
import unittest
from preparar_notebook.src.jupyter_notebook_to_html import add_index_html, add_content_html, format_anchor_links, format_images, replace_braces, img_base64_to_webp, add_witdh_and_height_to_image, convert_to_html

class Test_jupyter_notebook_to_html(unittest.TestCase):
    def setUp(self):
        self.html_file = "preparar_notebook/tests/test_jupyter_notebook_to_html.html"
        with open(self.html_file, "r") as file:
            self.html_content = file.read()
    
    def test_add_index_html(self):
        index_html = add_index_html(self.html_content)
        with open("preparar_notebook/tests/test_jupyter_notebook_to_html_index.html", "r") as file:
            true_index_html = file.read()

        # split the html content in lines
        index_html_lines = index_html.split("\n")
        true_index_html_lines = true_index_html.split("\n")
        for index, line in enumerate(true_index_html_lines):
            self.assertEqual(line, index_html_lines[index])

    def test_add_content_html(self):
        content_html = add_content_html(self.html_content)
        with open("preparar_notebook/tests/test_jupyter_notebook_to_html_content.html", "r") as file:
            true_content_html = file.read()

        # split the html content in lines
        content_html_lines = content_html.split("\n")
        true_content_html_lines = true_content_html.split("\n")
        for index, line in enumerate(true_content_html_lines):
            self.assertEqual(line, content_html_lines[index])
    
    def test_format_anchor_links_internal(self):
        html_content = "akdsjak\n<a href=\"https://maximofn.com\">MaximoFN</a>\ndasdaks"
        formatted_html_content = format_anchor_links(html_content)
        html_content = html_content + "\n"
        self.assertEqual(formatted_html_content, html_content)
    
    def test_format_anchor_links_external(self):
        html_content = "akdsjak\n<a href=\"https://google.com\">Google</a>\ndasdaks"
        html_external_content = "akdsjak\n<a href=\"https://google.com\" target=\"_blank\" rel=\"nofollow noreferrer\">Google</a>\ndasdaks\n"
        formatted_html_content = format_anchor_links(html_content)
        self.assertEqual(formatted_html_content, html_external_content)
