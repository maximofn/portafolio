import os
from unittest.mock import patch
import unittest
from preparar_notebook.src.jupyter_notebook_to_html import add_index_html, add_content_html, format_anchor_links, format_images, replace_braces, img_base64_to_webp, add_witdh_and_height_to_image, convert_to_html

class Test_jupyter_notebook_to_html(unittest.TestCase):
    def setUp(self):
        self.html_file = "preparar_notebook/tests/test_jupyter_notebook_to_html.html"
        with open(self.html_file, "r") as file:
            self.html_content = file.read()
        self.open_brace = "{"
        self.close_brace = "}"
        self.open_brace_formated = "{opening_brace}"
        self.close_brace_formated = "{closing_brace}"
    
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

    def test_format_images(self):
        html_content = "akdsjak\n<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/x+AAwMCAO+ip1sAAAAASUVORK5CYII=\">\ndasdaks"
        html_content_formatted = "akdsjak\n<img decoding=\"async\" src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/x+AAwMCAO+ip1sAAAAASUVORK5CYII=\">\ndasdaks\n"
        formatted_html_content = format_images(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {
    def test_replace_braces_with_opening_brace(self):
        html_content = "akdsjak\n<section>\n<p>{</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)
    
    # }
    def test_replace_braces_with_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.close_brace}</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.close_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)
    
    # {something}
    def test_replace_braces_with_opening_brace_and_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.open_brace}something{self.close_brace}</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}something{self.close_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {opening_brace}
    def test_replace_braces_with_formated_opening_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.open_brace_formated}</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {closing_brace}
    def test_replace_braces_with_formated_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.close_brace_formated}</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.close_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {opening_brace}something{closing_brace}
    def test_replace_braces_with_formated_opening_brace_and_formated_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.open_brace_formated}something{self.close_brace_formated}</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}something{self.close_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {something{opening_brace}
    def test_replace_braces_with_opening_brace_and_formated_opening_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.open_brace}something{self.open_brace_formated}something</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}something{self.open_brace_formated}something</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {something{closing_brace}
    def test_replace_braces_with_opening_brace_and_formated_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.open_brace}something{self.close_brace_formated}something</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}something{self.close_brace_formated}something</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # }something{opening_brace}
    def test_replace_braces_with_closing_brace_and_formated_opening_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.close_brace}something{self.open_brace_formated}something</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.close_brace_formated}something{self.open_brace_formated}something</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # }something{closing_brace}
    def test_replace_braces_with_closing_brace_and_formated_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.close_brace}something{self.close_brace_formated}something</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.close_brace_formated}something{self.close_brace_formated}something</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    # {something}something{opening_brace}something{closing_brace}
    def test_replace_braces_with_opening_brace_closing_brase_and_formated_opening_brace_and_formated_closing_brace(self):
        html_content = f"akdsjak\n<section>\n<p>{self.open_brace}something{self.close_brace}something{self.open_brace_formated}something{self.close_brace_formated}</p>\n</section>\ndasdaks"
        html_content_formatted = f"akdsjak\n<section>\n<p>{self.open_brace_formated}something{self.close_brace_formated}something{self.open_brace_formated}something{self.close_brace_formated}</p>\n</section>\ndasdaks\n"
        formatted_html_content = replace_braces(html_content)
        self.assertEqual(formatted_html_content, html_content_formatted)

    @unittest.skip('Not implemented yet')
    def test_img_base64_to_webp(self):
        # html_content = "akdsjak\n<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/x+AAwMCAO+ip1sAAAAASUVORK5CYII=\" alt=\"image test\">"
        # html_content_formatted = "akdsjak\n<img src=\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/x+AAwMCAO+ip1sAAAAASUVORK5CYII=\" alt=\"image test\">"
        # formatted_html_content = img_base64_to_webp(html_content, "test")
        # self.assertEqual(formatted_html_content, html_content_formatted)
        pass

    def test_add_witdh_and_height_to_image(self):
        img_url = "https://pub-fb664c455eca46a2ba762a065ac900f7.r2.dev/BPE_tokenizer.webp"
        html_content = f"akdsjak\n<img src=\"{img_url}\" alt=\"image test\">\ndasdaks"
        html_content_formatted = f"akdsjak\n<img src=\"{img_url}\" width=\"770\" height=\"728\" alt=\"image test\">\ndasdaks"
        formatted_html_content = add_witdh_and_height_to_image(html_content)
        html_content_formatted = html_content_formatted + "\n"
        self.assertEqual(formatted_html_content, html_content_formatted)