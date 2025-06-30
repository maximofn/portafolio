import os
import unittest
import sys
import json # Added from test_markdown_code_to_html.py
import shutil # Added from test_markdown_code_to_html.py
import tempfile # Added from test_markdown_code_to_html.py
from pathlib import Path # Added from test_markdown_code_to_html.py

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # From test_markdown_code_to_html.py, slightly different but achieves similar goal

from generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns
from src.markdown_to_html.markdown_code_to_html_converter import markdown_code_to_html
from src.markdown_to_html.markdown_image_to_html import markdown_image_to_html
from src.markdown_to_html.markdown_link_to_html import markdown_to_html_external_link, markdown_to_html_internal_link
from src.markdown_to_html.markdown_lists_to_html import markdown_to_html_updated # Using the refined function
from src.markdown_to_html.markdown_table_to_html import markdown_table_to_html

class TestGenericMarkdownToSpecificMarkdowns(unittest.TestCase): # Renamed from TestMarkdownCodeToHtml to avoid conflict
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_text_markdown(self):
        markdown_content = "This is a text markdown"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['This is a text markdown'])

    def test_code_markdown(self):
        markdown_content = "```python\nprint('hello world')\n```"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['```python\nprint(\'hello world\')\n```'])

    def test_table_markdown(self):
        markdown_content = "| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |\n| Data 4   | Data 5   | Data 6   |"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |\n| Data 4   | Data 5   | Data 6   |'])

    def test_list_markdown_guion(self):
        markdown_content = " - Item 1\n - Item 2\n - Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [' - Item 1\n - Item 2\n - Item 3\n'])

    def test_list_markdown_asterisk(self):
        markdown_content = " * Item 1\n * Item 2\n * Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [' * Item 1\n * Item 2\n * Item 3\n'])

    def test_list_markdown_plus(self):
        markdown_content = " + Item 1\n + Item 2\n + Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [' + Item 1\n + Item 2\n + Item 3\n'])

    def test_list_markdown_number(self):
        markdown_content = " 1. Item 1\n 2. Item 2\n 3. Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [' 1. Item 1\n 2. Item 2\n 3. Item 3\n'])

    def test_external_url_markdown(self):
        markdown_content = "[Link](https://www.google.com)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['[Link](https://www.google.com)'])

    def test_internal_es_link_markdown(self):
        markdown_content = "[Link](https://www.maximofn.com/blog)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['[Link](/blog)'])

    def test_internal_en_link_markdown(self):
        markdown_content = "[Link](https://www.maximofn.com/en/blog/)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['[Link](/en/blog/)'])

    def test_internal_pt_link_markdown(self):
        markdown_content = "[Link](https://www.maximofn.com/pt-br/blog/)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['[Link](/pt-br/blog/)'])

    def test_image_markdown(self):
        markdown_content = "![Image](image.png)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, ['![Image](image.png)'])

    def test_generic_markdown(self):
        markdown_content = """This is a text markdown

```python
print('hello world')
```

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

 - Item 1
 - Item 2
 - Item 3

 + Item 1
 + Item 2
 + Item 3

 1. Item 1
 2. Item 2
 3. Item 3

[Link](https://www.google.com)

[Link](https://www.maximofn.com/blog)

[Link](https://www.maximofn.com/en/blog/)

[Link](https://www.maximofn.com/pt-br/blog/)

![Image](image.png)"""
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        expected_specific_markdowns = [
            "This is a text markdown",
            "```python\nprint(\'hello world\')\n```",
            "| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |\n| Data 4   | Data 5   | Data 6   |\n",
            " - Item 1\n - Item 2\n - Item 3\n",
            " + Item 1\n + Item 2\n + Item 3\n",
            " 1. Item 1\n 2. Item 2\n 3. Item 3\n",
            "[Link](https://www.google.com)",
            "[Link](/blog)",
            "[Link](/en/blog/)",
            "[Link](/pt-br/blog/)",
            "![Image](image.png)",
        ]
        self.assertEqual(specific_markdowns, expected_specific_markdowns)

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

class TestMarkdownImageToHtml(unittest.TestCase):

    def test_valid_markdown_image(self):
        markdown = "![alt text](image.png)"
        expected_html = '<img src="image.png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_url_and_alt_text_in_sentence(self):
        markdown = "An image ![alt text for image](http://example.com/img.jpg) in a sentence."
        expected_html = 'An image <img src="http://example.com/img.jpg" alt="alt text for image"> in a sentence.'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_empty_alt_text(self):
        markdown = "![](image_no_alt.gif)"
        expected_html = '<img src="image_no_alt.gif" alt="">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_spaces_in_url(self):
        markdown = "![alt text](my image path.png)"
        expected_html = '<img src="my image path.png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_multiple_images_in_one_line(self):
        markdown = "![alt1](url1.png) and ![alt2](url2.jpg)"
        expected_html = '<img src="url1.png" alt="alt1"> and <img src="url2.jpg" alt="alt2">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_no_markdown_image_present(self):
        markdown = "This is a regular text without any image."
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_empty_string_input(self):
        markdown = ""
        self.assertEqual(markdown_image_to_html(markdown), "")

    def test_markdown_image_missing_url(self):
        markdown = "![alt text]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_malformed_markdown_no_closing_parenthesis_for_url(self):
        markdown = "![alt text](image.png"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_malformed_markdown_no_closing_bracket_for_alt_text(self):
        markdown = "![alt text(image.png)"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_text_that_looks_like_image_but_is_not_markdown_link(self):
        markdown = "This is not an image: [alt text](image.png)"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_image_at_start_of_string(self):
        markdown = "![alt text](image.png) Some following text."
        expected_html = '<img src="image.png" alt="alt text"> Some following text.'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_at_end_of_string(self):
        markdown = "Some preceding text. ![alt text](image.png)"
        expected_html = 'Some preceding text. <img src="image.png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_relative_path(self):
        markdown = "![logo](../images/logo.svg)"
        expected_html = '<img src="../images/logo.svg" alt="logo">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_query_parameters_in_url(self):
        markdown = "![tracking pixel](pixel.gif?id=123&user=abc)"
        expected_html = '<img src="pixel.gif?id=123&user=abc" alt="tracking pixel">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_inside_a_link_like_construct_but_still_image(self):
        markdown = "[![alt text](image.png)](destination_url)"
        expected_html = '[<img src="image.png" alt="alt text">](destination_url)'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_only_exclamation_and_brackets_no_parentheses(self):
        markdown = "![alt text]"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_exclamation_brackets_empty_parentheses(self):
        markdown = "![alt text]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_no_alt_text_no_url(self):
        markdown = "![]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_alt_text_contains_brackets(self):
        markdown = "![alt [text] here](image.png)"
        expected_html = '<img src="image.png" alt="alt [text] here">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_url_contains_parentheses_not_supported_by_simple_regex(self):
        markdown = "![alt text](http://example.com/path(with_parens).png)"
        expected_html = '<img src="http://example.com/path(with_parens" alt="alt text">.png)'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

class TestMarkdownLinkToHtml(unittest.TestCase):

    def test_markdown_to_html_external_link(self):
        self.assertEqual(
            markdown_to_html_external_link("[Google](https://google.com)"),
            '<a href="https://google.com">Google</a>'
        )
        self.assertEqual(
            markdown_to_html_external_link("[Example Site](http://example.com)"),
            '<a href="http://example.com">Example Site</a>'
        )
        self.assertEqual(
            markdown_to_html_external_link("[No Protocol](google.com)"),
            "[No Protocol](google.com)"
        )
        self.assertEqual(
            markdown_to_html_external_link("Not a link"),
            "Not a link"
        )
        self.assertEqual(
            markdown_to_html_external_link("[Missing URL]()"),
            "[Missing URL]()"
        )
        self.assertEqual(
            markdown_to_html_external_link("[](https://example.com)"),
            '<a href="https://example.com"></a>'
        )

    def test_markdown_to_html_internal_link(self):
        self.assertEqual(
            markdown_to_html_internal_link("[Homepage](/home)"),
            '<a href="/home">Homepage</a>'
        )
        self.assertEqual(
            markdown_to_html_internal_link("[About Us](/about-us)"),
            '<a href="/about-us">About Us</a>'
        )
        self.assertEqual(
            markdown_to_html_internal_link("[Docs](/docs/api)"),
            '<a href="/docs/api">Docs</a>'
        )
        self.assertEqual(
            markdown_to_html_internal_link("[Google](https://google.com)"),
            "[Google](https://google.com)"
        )
        self.assertEqual(
            markdown_to_html_internal_link("Not a link"),
            "Not a link"
        )
        self.assertEqual(
            markdown_to_html_internal_link("[Missing URL]()"),
            "[Missing URL]()"
        )
        self.assertEqual(
            markdown_to_html_internal_link("[](/internal-page)"),
            '<a href="/internal-page"></a>'
        )

class TestMarkdownUnorderedListToHtml(unittest.TestCase):

    def test_simple_list_hyphen(self):
        markdown = "- item 1\n- item 2\n- item 3"
        expected_html = "<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n  <li>item 3</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_simple_list_asterisk(self):
        markdown = "* item A\n* item B"
        expected_html = "<ul>\n  <li>item A</li>\n  <li>item B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_simple_list_plus(self):
        markdown = "+ entry 1\n+ entry 2"
        expected_html = "<ul>\n  <li>entry 1</li>\n  <li>entry 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_mixed_markers_simple_list(self):
        markdown = "- item 1\n* item 2\n+ item 3"
        expected_html = "<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n  <li>item 3</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_list_hyphen(self):
        markdown = "- level 1 item 1\n  - level 2 item 1\n  - level 2 item 2\n- level 1 item 2"
        expected_html = "<ul>\n  <li>level 1 item 1</li>\n  <ul>\n    <li>level 2 item 1</li>\n    <li>level 2 item 2</li>\n  </ul>\n  <li>level 1 item 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_list_asterisk(self):
        markdown = "* level 1 item A\n  * level 2 item A\n* level 1 item B"
        expected_html = "<ul>\n  <li>level 1 item A</li>\n  <ul>\n    <li>level 2 item A</li>\n  </ul>\n  <li>level 1 item B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_deeply_nested_list(self):
        markdown = "- L1\n  - L2\n    - L3\n      - L4\n- L1B"
        expected_html = "<ul>\n  <li>L1</li>\n  <ul>\n    <li>L2</li>\n    <ul>\n      <li>L3</li>\n      <ul>\n        <li>L4</li>\n      </ul>\n    </ul>\n  </ul>\n  <li>L1B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_list_mixed_markers(self):
        markdown = "- First level item\n  * Second level item\n    + Third level item\n- Another first level item"
        expected_html = "<ul>\n  <li>First level item</li>\n  <ul>\n    <li>Second level item</li>\n    <ul>\n      <li>Third level item</li>\n    </ul>\n  </ul>\n  <li>Another first level item</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_with_varied_indentation_and_markers(self):
        markdown = (
            "* Root A\n"
            "  - Child A1\n"
            "  - Child A2\n"
            "    + Grandchild A2a\n"
            "* Root B\n"
            "  - Child B1"
        )
        expected_html = (
            "<ul>\n"
            "  <li>Root A</li>\n"
            "  <ul>\n"
            "    <li>Child A1</li>\n"
            "    <li>Child A2</li>\n"
            "    <ul>\n"
            "      <li>Grandchild A2a</li>\n"
            "    </ul>\n"
            "  </ul>\n"
            "  <li>Root B</li>\n"
            "  <ul>\n"
            "    <li>Child B1</li>\n"
            "  </ul>\n"
            "</ul>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_empty_input(self):
        markdown = ""
        expected_html = ""
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_input_with_only_whitespace(self):
        markdown = "   \n  \n "
        expected_html = ""
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_input_not_a_list(self):
        markdown = "This is a paragraph."
        expected_html = "<p>This is a paragraph.</p>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_with_surrounding_text(self):
        markdown = "Intro text\n- item 1\n- item 2\nOutro text"
        expected_html = "<p>Intro text</p>\n<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n</ul>\n<p>Outro text</p>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_items_with_leading_trailing_spaces(self):
        markdown = "-   item 1 with spaces  \n- item 2  "
        expected_html = "<ul>\n  <li>item 1 with spaces</li>\n  <li>item 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_incorrect_indentation_resets_list(self):
        markdown = (
            "- Level 1\n"
            "  - Level 2\n"
            "    - Level 3\n"
            " - Incorrectly indented Level 1 (should be new list or error, current logic makes it a new L0 list)"
        )
        expected_html = (
            "<ul>\n"
            "  <li>Level 1</li>\n"
            "  <ul>\n"
            "    <li>Level 2</li>\n"
            "    <ul>\n"
            "      <li>Level 3</li>\n"
            "    </ul>\n"
            "  </ul>\n"
            "  <li>Incorrectly indented Level 1 (should be new list or error, current logic makes it a new L0 list)</li>\n"
            "</ul>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_ending_with_nested_item(self):
        markdown = "- item 1\n  - item 1.1"
        expected_html = "<ul>\n  <li>item 1</li>\n  <ul>\n    <li>item 1.1</li>\n  </ul>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_with_blank_lines_between_items(self):
        markdown = "- item 1\n\n- item 2"
        expected_html = "<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_starts_with_indentation(self):
        markdown = "  - indented item"
        expected_html = "<ul>\n  <li>indented item</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown).strip(), expected_html.strip())


class TestMarkdownOrderedListToHtml(unittest.TestCase):

    def test_simple_ordered_list(self):
        markdown = "1. Item 1\n2. Item 2\n3. Item 3"
        expected_html = "<ol>\n  <li>Item 1</li>\n  <li>Item 2</li>\n  <li>Item 3</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_with_different_starting_number(self):
        markdown = "3. Item A\n4. Item B"
        expected_html = "<ol>\n  <li>Item A</li>\n  <li>Item B</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_with_non_sequential_numbers(self):
        markdown = "1. First\n3. Third\n2. Second"
        expected_html = "<ol>\n  <li>First</li>\n  <li>Third</li>\n  <li>Second</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_ordered_list(self):
        markdown = "1. Level 1 Item 1\n  1. Level 2 Item 1\n  2. Level 2 Item 2\n2. Level 1 Item 2"
        expected_html = "<ol>\n  <li>Level 1 Item 1</li>\n  <ol>\n    <li>Level 2 Item 1</li>\n    <li>Level 2 Item 2</li>\n  </ol>\n  <li>Level 1 Item 2</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_deeply_nested_ordered_list(self):
        markdown = "1. L1\n  1. L2\n    1. L3\n      1. L4\n2. L1B"
        expected_html = "<ol>\n  <li>L1</li>\n  <ol>\n    <li>L2</li>\n    <ol>\n      <li>L3</li>\n      <ol>\n        <li>L4</li>\n      </ol>\n    </ol>\n  </ol>\n  <li>L1B</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_ending_with_nested_item(self):
        markdown = "1. item 1\n  1. item 1.1"
        expected_html = "<ol>\n  <li>item 1</li>\n  <ol>\n    <li>item 1.1</li>\n  </ol>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_with_leading_trailing_spaces_in_items(self):
        markdown = "1.   item 1 with spaces  \n2. item 2  "
        expected_html = "<ol>\n  <li>item 1 with spaces</li>\n  <li>item 2</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_starts_with_indentation(self):
        markdown = "  1. indented item"
        expected_html = "<ol>\n  <li>indented item</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown).strip(), expected_html.strip())


class TestMixedMarkdownListsToHtml(unittest.TestCase):

    def test_mixed_list_simple(self):
        markdown = "- Unordered 1\n1. Ordered 1\n- Unordered 2\n2. Ordered 2"
        expected_html = "<ul>\n  <li>Unordered 1</li>\n</ul>\n<ol>\n  <li>Ordered 1</li>\n</ol>\n<ul>\n  <li>Unordered 2</li>\n</ul>\n<ol>\n  <li>Ordered 2</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_mixed_list_with_nesting(self):
        markdown = (
            "1. Ordered L1 A\n"
            "  - Unordered L2 A.1\n"
            "  - Unordered L2 A.2\n"
            "2. Ordered L1 B\n"
            "  1. Ordered L2 B.1\n"
            "    * Unordered L3 B.1.a\n"
            "  2. Ordered L2 B.2"
        )
        expected_html = (
            "<ol>\n"
            "  <li>Ordered L1 A</li>\n"
            "  <ul>\n"
            "    <li>Unordered L2 A.1</li>\n"
            "    <li>Unordered L2 A.2</li>\n"
            "  </ul>\n"
            "  <li>Ordered L1 B</li>\n"
            "  <ol>\n"
            "    <li>Ordered L2 B.1</li>\n"
            "    <ul>\n"
            "      <li>Unordered L3 B.1.a</li>\n"
            "    </ul>\n"
            "    <li>Ordered L2 B.2</li>\n"
            "  </ol>\n"
            "</ol>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_interspersed_with_text(self):
        markdown = "Paragraph 1.\n\n1. Item 1\n2. Item 2\n\nAnother paragraph.\n\n- Unordered A\n- Unordered B"
        expected_html = "<p>Paragraph 1.</p>\n<ol>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ol>\n<p>Another paragraph.</p>\n<ul>\n  <li>Unordered A</li>\n  <li>Unordered B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_complex_nesting_and_switching(self):
        markdown = (
            "- U1\n"
            "  1. O2_A\n"
            "    - U3_A1\n"
            "    - U3_A2\n"
            "  2. O2_B\n"
            "- U1_Next\n"
            "1. O1_Separate"
        )
        expected_html = (
            "<ul>\n"
            "  <li>U1</li>\n"
            "  <ol>\n"
            "    <li>O2_A</li>\n"
            "    <ul>\n"
            "      <li>U3_A1</li>\n"
            "      <li>U3_A2</li>\n"
            "    </ul>\n"
            "    <li>O2_B</li>\n"
            "  </ol>\n"
            "  <li>U1_Next</li>\n"
            "</ul>\n"
            "<ol>\n"
            "  <li>O1_Separate</li>\n"
            "</ol>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

class TestMarkdownTableToHtml(unittest.TestCase):

    def test_basic_table(self):
        markdown = """
| Header 1 | Header 2 |
| -------- | -------- |
| Row 1 Col 1 | Row 1 Col 2 |
| Row 2 Col 1 | Row 2 Col 2 |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Row 1 Col 1</td>
      <td>Row 1 Col 2</td>
    </tr>
    <tr>
      <td>Row 2 Col 1</td>
      <td>Row 2 Col 2</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_table_with_alignment(self):
        markdown = """
| Left Align | Center Align | Right Align |
| :------- | :------: | --------: |
| L1       | C1       | R1        |
| L2       | C2       | R2        |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Left Align</th>
      <th style="text-align: center;">Center Align</th>
      <th style="text-align: right;">Right Align</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>L1</td>
      <td style="text-align: center;">C1</td>
      <td style="text-align: right;">R1</td>
    </tr>
    <tr>
      <td>L2</td>
      <td style="text-align: center;">C2</td>
      <td style="text-align: right;">R2</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())


    def test_table_with_empty_cells(self):
        markdown = """
| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| A        |          | C        |
|          | E        | F        |
| G        | H        |          |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
      <th>Header 3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>A</td>
      <td></td>
      <td>C</td>
    </tr>
    <tr>
      <td></td>
      <td>E</td>
      <td>F</td>
    </tr>
    <tr>
      <td>G</td>
      <td>H</td>
      <td></td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_table_with_inline_markdown(self):
        markdown = """
| Header 1 | Header 2 |
| -------- | -------- |
| *Italic* | **Bold** |
| `Code`   | [Link](http://example.com) |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>*Italic*</td>
      <td>**Bold**</td>
    </tr>
    <tr>
      <td>`Code`</td>
      <td>[Link](http://example.com)</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_single_row_table(self):
        markdown = """
| Header |
| ------ |
| Data   |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_no_data_rows_table(self):
        markdown = """
| Header 1 | Header 2 |
| -------- | -------- |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_malformed_separator_less_columns(self):
        markdown = """
| H1 | H2 | H3 |
| -- | -- |
| D1 | D2 | D3 |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>H1</th>
      <th>H2</th>
      <th>H3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>D1</td>
      <td>D2</td>
      <td>D3</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())


    def test_table_no_leading_trailing_pipes_in_header(self):
        markdown = """
Header 1 | Header 2
-------- | --------
Row 1 Col 1 | Row 1 Col 2
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Row 1 Col 1</td>
      <td>Row 1 Col 2</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_table_no_leading_trailing_pipes_in_data(self):
        markdown = """
| Header 1 | Header 2 |
| -------- | -------- |
Row 1 Col 1 | Row 1 Col 2
Row 2 Col 1 | Row 2 Col 2
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Row 1 Col 1</td>
      <td>Row 1 Col 2</td>
    </tr>
    <tr>
      <td>Row 2 Col 1</td>
      <td>Row 2 Col 2</td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_table_mixed_pipe_usage(self):
        markdown = """
Header 1 | Header 2
:-------- | --------:
| Val 1   | Val 2
Val 3   | Val 4 |
| Val 5 |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th style="text-align: right;">Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Val 1</td>
      <td style="text-align: right;">Val 2</td>
    </tr>
    <tr>
      <td>Val 3</td>
      <td style="text-align: right;">Val 4</td>
    </tr>
    <tr>
      <td>Val 5</td>
      <td style="text-align: right;"></td>
    </tr>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

    def test_empty_input_table(self): # Renamed to avoid conflict
        self.assertEqual(markdown_table_to_html(""), "")

    def test_only_header_table(self): # Renamed to avoid conflict
        markdown = "| H1 | H2 |"
        self.assertEqual(markdown_table_to_html(markdown), "")

    def test_header_and_malformed_separator_table(self): # Renamed to avoid conflict
        markdown = """
| H1 | H2 |
| --xx-- | --yy-- |
"""
        expected_html = """<table>
  <thead>
    <tr>
      <th>H1</th>
      <th>H2</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>"""
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
