import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.jupyter_notebook_to_html.jupyter_notebook_to_html import output_code_to_html

class TestOutputCodeToHtml(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one_line(self):
        output_code = "Detected language: en"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>Detected language: en
</pre>
</div>
</div>
</div>
</section>'''
        self.assertEqual(output_code_to_html(output_code), expected_html)

if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
