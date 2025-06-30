import unittest
from preparar_notebook.src.markdown_table_to_html import markdown_table_to_html

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
        # The current function does not process inline markdown within cells,
        # it treats cell content as plain text. This test reflects that.
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
        # Test when separator line implies fewer columns than header
        markdown = """
| H1 | H2 | H3 |
| -- | -- |
| D1 | D2 | D3 |
"""
        # Expects it to try its best, padding with default alignment (left) for missing ones
        # and potentially adding empty cells if data implies more columns.
        # Current implementation might default all to left if separator is too malformed.
        # This test checks the current behavior.
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
        # Note: The parser might struggle with inconsistent missing cells vs. header count.
        # This tests its robustness.
        # Expected might need adjustment based on how robust the parser is.
        # For Val 5, it should ideally pad the second cell.
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

    def test_empty_input(self):
        self.assertEqual(markdown_table_to_html(""), "")

    def test_only_header(self):
        # Invalid markdown table, but test behavior
        markdown = "| H1 | H2 |"
        self.assertEqual(markdown_table_to_html(markdown), "") # Expect empty as it's not a valid table

    def test_header_and_malformed_separator(self):
        markdown = """
| H1 | H2 |
| --xx-- | --yy-- |
"""
        # Expects default left alignment due to malformed separator markers
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
    unittest.main()
