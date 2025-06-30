import unittest
from src.markdown_link_to_html import markdown_to_html_external_link, markdown_to_html_internal_link

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
        # Test with no protocol (should not convert as it's not a valid external link by current definition)
        self.assertEqual(
            markdown_to_html_external_link("[No Protocol](google.com)"),
            "[No Protocol](google.com)"
        )
        # Test invalid format
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
        # Test with subdirectories
        self.assertEqual(
            markdown_to_html_internal_link("[Docs](/docs/api)"),
            '<a href="/docs/api">Docs</a>'
        )
        # Test invalid format (external link)
        self.assertEqual(
            markdown_to_html_internal_link("[Google](https://google.com)"),
            "[Google](https://google.com)"
        )
        # Test invalid format
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

if __name__ == '__main__':
    unittest.main()
