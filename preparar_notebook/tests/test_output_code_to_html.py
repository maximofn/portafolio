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
    
    def test_one_line_with_endline_at_the_end(self):
        output_code = "Detected language: en\n"
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
    
    def test_micromachines_output(self):
        output_code = '"This is the Micro Machine Man presenting the most midget miniature motorcade of micro machines. Each one has dramatic details, terrific trim, precision paint jobs, plus incredible micro machine pocket play sets. There\'s a police station, fire station, restaurant, service station, and more. Perfect pocket portables to take any place. And there are many miniature play sets to play with and each one comes with its own special edition micro machine vehicle and fun fantastic features that miraculously move. Raise the boat lift at the airport, marina, man the gun turret at the army base, clean your car at the car wash, raise the toll bridge. And these play sets fit together to form a micro machine world. Micro machine pocket play sets so tremendously tiny, so perfectly precise, so dazzlingly detailed, you\'ll want to pocket them all. Micro machines and micro machine pocket play sets sold separately from Galoob. The smaller they are, the better they are."'
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt-output-prompt">Out[]:</div>
<div class="output-text-output-subareaoutput_execute_result">
<pre>&quot;This is the Micro Machine Man presenting the most midget miniature motorcade of micro machines. Each one has dramatic details, terrific trim, precision paint jobs, plus incredible micro machine pocket play sets. There&#x27;s a police station, fire station, restaurant, service station, and more. Perfect pocket portables to take any place. And there are many miniature play sets to play with and each one comes with its own special edition micro machine vehicle and fun fantastic features that miraculously move. Raise the boat lift at the airport, marina, man the gun turret at the army base, clean your car at the car wash, raise the toll bridge. And these play sets fit together to form a micro machine world. Micro machine pocket play sets so tremendously tiny, so perfectly precise, so dazzlingly detailed, you&#x27;ll want to pocket them all. Micro machines and micro machine pocket play sets sold separately from Galoob. The smaller they are, the better they are.&quot;</pre>
</div>
</div>
</div>
</section>'''
        self.assertEqual(output_code_to_html(output_code), expected_html)
    
    def test_output_code_with_multiple_lines_and_indentation(self):
        output_code = "[{'score': 0.05116177722811699,\n  'token': 8422,\n  'token_str': 'stanford',\n  'sequence': 'i am a student at stanford university.'},\n {'score': 0.04033993184566498,\n  'token': 5765,\n  'token_str': 'harvard',\n  'sequence': 'i am a student at harvard university.'},\n {'score': 0.03990468755364418,\n  'token': 7996,\n  'token_str': 'yale',\n  'sequence': 'i am a student at yale university.'},\n {'score': 0.0361952930688858,\n  'token': 10921,\n  'token_str': 'cornell',\n  'sequence': 'i am a student at cornell university.'},\n {'score': 0.03303057327866554,\n  'token': 9173,\n  'token_str': 'princeton',\n  'sequence': 'i am a student at princeton university.'}]"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>[&#x7B;&#x27;score&#x27;: 0.05116177722811699,
&#x20;&#x20;&#x27;token&#x27;: 8422,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;stanford&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at stanford university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.04033993184566498,
&#x20;&#x20;&#x27;token&#x27;: 5765,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;harvard&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at harvard university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.03990468755364418,
&#x20;&#x20;&#x27;token&#x27;: 7996,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;yale&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at yale university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.0361952930688858,
&#x20;&#x20;&#x27;token&#x27;: 10921,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;cornell&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at cornell university.&#x27;&#x7D;,
 &#x7B;&#x27;score&#x27;: 0.03303057327866554,
&#x20;&#x20;&#x27;token&#x27;: 9173,
&#x20;&#x20;&#x27;token_str&#x27;: &#x27;princeton&#x27;,
&#x20;&#x20;&#x27;sequence&#x27;: &#x27;i am a student at princeton university.&#x27;&#x7D;]
</pre>
</div>
</div>
</div>
</section>'''
        html_output = output_code_to_html(output_code)
        self.assertEqual(html_output, expected_html)

    def test_output_code_with_ansi_escape_code(self):
        output_code = "Cloning into 'LLMs-from-scratch'...\nremote: Enumerating objects: 260, done.\x1b[K\nremote: Counting objects: 100% (260/260), done.\x1b[K\nremote: Compressing objects: 100% (226/226), done.\x1b[K\nremote: Total 260 (delta 61), reused 121 (delta 22), pack-reused 0 (from 0)\x1b[K\nReceiving objects: 100% (260/260), 1.64 MiB | 6.94 MiB/s, done.\nResolving deltas: 100% (61/61), done.\n"
        expected_html = '''<section class="section-block-code-cell-">
<div class="output-wrapper">
<div class="output-area">
<div class="prompt"></div>
<div class="output-subarea-output-stream-output-stdout-output-text">
<pre>Cloning into &#x27;LLMs-from-scratch&#x27;...
remote: Enumerating objects: 260, done.
remote: Counting objects: 100% (260/260), done.
remote: Compressing objects: 100% (226/226), done.
remote: Total 260 (delta 61), reused 121 (delta 22), pack-reused 0 (from 0)
Receiving objects: 100% (260/260), 1.64 MiB | 6.94 MiB/s, done.
Resolving deltas: 100% (61/61), done.
</pre>
</div>
</div>
</div>
</section>'''
        html_output = output_code_to_html(output_code)
        self.assertEqual(html_output, expected_html)



if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
