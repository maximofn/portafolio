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

if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
