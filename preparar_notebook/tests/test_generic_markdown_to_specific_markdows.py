import os
import unittest

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns

class TestMarkdownCodeToHtml(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
