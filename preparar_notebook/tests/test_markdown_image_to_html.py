import os
import unittest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.markdown_to_html.markdown_image_to_html import markdown_image_to_html

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
        # This is considered malformed by the function and should be returned as is.
        markdown = "![alt text]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_malformed_markdown_no_closing_parenthesis_for_url(self):
        markdown = "![alt text](image.png" # Missing closing ')'
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_malformed_markdown_no_closing_bracket_for_alt_text(self):
        markdown = "![alt text(image.png)" # Missing closing ']'
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_text_that_looks_like_image_but_is_not_markdown_link(self):
        markdown = "This is not an image: [alt text](image.png)" # Missing '!'
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
        # This is a bit of an edge case, but valid markdown image syntax
        markdown = "[![alt text](image.png)](destination_url)"
        expected_html = '[<img src="image.png" alt="alt text">](destination_url)'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_only_exclamation_and_brackets_no_parentheses(self):
        markdown = "![alt text]"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_exclamation_brackets_empty_parentheses(self):
        markdown = "![alt text]()" # This is already tested in test_markdown_image_missing_url
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_no_alt_text_no_url(self):
        markdown = "![]()" # This is also tested in test_markdown_image_missing_url (url is primary concern)
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_alt_text_contains_brackets(self):
        markdown = "![alt [text] here](image.png)"
        expected_html = '<img src="image.png" alt="alt [text] here">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_url_contains_parentheses_not_supported_by_simple_regex(self):
        # Standard markdown might allow balanced parentheses in URLs if percent-encoded,
        # but a simple regex like (.*?) might capture greedily or incorrectly.
        # The current regex r"!\[(.*?)\]\((.*?)\)" is non-greedy for URL, so it stops at the first ')'
        markdown = "![alt text](http://example.com/path(with_parens).png)"
        # Expected behavior with current regex: it will only capture up to 'path(with_parens)'
        # and '.png)' will be outside the match. This is a limitation.
        # A more robust parser would handle balanced parentheses.
        # For this test, we expect the current regex behavior:
        # The non-greedy (.*?) for URL will stop at the first ')' it sees.
        expected_html = '<img src="http://example.com/path(with_parens" alt="alt text">.png)'
        # If the regex was r"!\[(.*?)\]\((.*)\)" (greedy), it would be different.
        # Let's test current non-greedy behavior.
        self.assertEqual(markdown_image_to_html(markdown), expected_html)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
