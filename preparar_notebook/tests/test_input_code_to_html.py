import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.jupyter_notebook_to_html.jupyter_notebook_to_html import input_code_to_html

class TestInputCodeToHtml(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one_line_import(self):
        input_code = "import whisper"
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="kn">import</span><span class="w"> </span><span class="nn">whisper</span>
</pre></div>
</div>
</section>'''
        self.assertEqual(input_code_to_html(input_code), expected_html)
    
    def test_ampersand_in_code(self):
        input_code = "'!sudo apt update &amp;&amp; sudo apt install ffmpeg'"
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="err">!</span><span class="n">sudo</span> <span class="n">apt</span> <span class="n">update</span> <span class="o">&amp;</span></span><span class="o">&amp;</span> <span class="n">sudo</span> <span class="n">apt</span> <span class="n">install</span> <span class="n">ffmpeg</span>
</pre></div>
</div>
</section>'''
        self.assertEqual(input_code_to_html(input_code), expected_html)

if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
