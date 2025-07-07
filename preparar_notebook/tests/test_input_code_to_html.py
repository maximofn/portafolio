import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from jupyter_notebook_to_html.jupyter_notebook_to_html import input_code_to_html

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
<div class="highlight hl-ipython3"><pre><span></span><span class="s1">&#39;!sudo apt update &amp;amp;&amp;amp; sudo apt install ffmpeg&#39;</span>
</pre></div>
</div>
</section>'''
        html = input_code_to_html(input_code)
        self.assertEqual(html, expected_html)
    
    def test_multiple_lines_bash_code(self):
        input_code = "'!sudo apt update &amp;&amp; sudo apt install ffmpeg'"
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="s1">&#39;!sudo apt update &amp;amp;&amp;amp; sudo apt install ffmpeg&#39;</span>
</pre></div>
</div>
</section>'''
        html = input_code_to_html(input_code)
        self.assertEqual(html, expected_html)
    
    def test_multiple_lines_python_code_with_indentation(self):
        input_code = 'from huggingface_hub import InferenceClient\n\nclient = InferenceClient(\n\tprovider="replicate",\n\tapi_key=REPLICATE_API_KEY,\n\ttimeout=1000\n)'
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="kn">from</span><span class="w"> </span><span class="nn">huggingface_hub</span><span class="w"> </span><span class="kn">import</span> <span class="n">InferenceClient</span>
<span class="w"> </span>
<span class="n">client</span> <span class="o">=</span> <span class="n">InferenceClient</span><span class="p">(</span>
<span class="w">	</span><span class="n">provider</span><span class="o">=</span><span class="s2">&quot;replicate&quot;</span><span class="p">,</span>
<span class="w">	</span><span class="n">api_key</span><span class="o">=</span><span class="n">REPLICATE_API_KEY</span><span class="p">,</span>
<span class="w">	</span><span class="n">timeout</span><span class="o">=</span><span class="mi">1000</span>
<span class="p">)</span>
</pre></div>
</div>
</section>'''
        html = input_code_to_html(input_code)
        self.assertEqual(html, expected_html)
    
    def test_multiple_lines_python_code_with_indentation_function(self):
        input_code = 'def encode_decode(word):\n    tokens = encoder.encode(word)\n    decode_tokens = []\n    for token in tokens:\n        decode_tokens.append(encoder.decode([token]))\n    return tokens, decode_tokens'
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="k">def</span><span class="w"> </span><span class="nf">encode_decode</span><span class="p">(</span><span class="n">word</span><span class="p">):</span>
<span class="w">    </span><span class="n">tokens</span> <span class="o">=</span> <span class="n">encoder</span><span class="o">.</span><span class="n">encode</span><span class="p">(</span><span class="n">word</span><span class="p">)</span>
<span class="w">    </span><span class="n">decode_tokens</span> <span class="o">=</span> <span class="p">[]</span>
<span class="w">    </span><span class="k">for</span> <span class="n">token</span> <span class="ow">in</span> <span class="n">tokens</span><span class="p">:</span>
<span class="w">        </span><span class="n">decode_tokens</span><span class="o">.</span><span class="n">append</span><span class="p">(</span><span class="n">encoder</span><span class="o">.</span><span class="n">decode</span><span class="p">([</span><span class="n">token</span><span class="p">]))</span>
<span class="w">    </span><span class="k">return</span> <span class="n">tokens</span><span class="p">,</span> <span class="n">decode_tokens</span>
</pre></div>
</div>
</section>'''
        html = input_code_to_html(input_code)
        self.assertEqual(html, expected_html)

if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
