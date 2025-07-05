from unittest.mock import patch
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from format_code_blocks import remove_empty_lines, format_code_blocks, format_input_code_block, format_output_code_block

class Test_format_code_blocks(unittest.TestCase):
    def test_remove_empty_lines_with_empty_lines(self):
        lines = [
            "",
            "></CodeBlockOutputCell>",
            "",
            "",
            "",
            "",
            "",
            "end"]
        lines_without_empty_lines = [
            '',
            '></CodeBlockOutputCell>',
            'end'
        ]
        lines, lines_removed = remove_empty_lines(lines)
        self.assertEqual(lines, lines_without_empty_lines)
        self.assertTrue(lines_removed)
    
    def test_remove_empty_lines_without_empty_lines(self):
        lines = [
            '></CodeBlockOutputCell>',
            'end'
        ]
        lines_without_empty_lines, lines_removed = remove_empty_lines(lines)
        self.assertEqual(lines_without_empty_lines, lines)
        self.assertFalse(lines_removed)
    
    def test_format_code_blocks_example1(self):
        #       <section class="section-block-code-cell-">
        #       <div class="input-code">
        #       <div class="highlight hl-ipython3">
        # <pre><span></span><span class="kn">import</span> <span class="nn">os</span>
        #       <span class="kn">import</span> <span class="nn">dotenv</span>
        #       
        #       <span class="n">dotenv</span><span class="o">.</span><span class="n">load_dotenv</span><span class="p">()</span>
        #       
        #       <span class="n">RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">getenv</span><span class="p">(</span><span class="s2">"RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN"</span><span class="p">)</span>
        #       </pre></div>
        #       </div>
        #       </section>
        content = '      <section class="section-block-code-cell-">'
        content = content + "\n" + '      <div class="input-code">'
        content = content + "\n" + '      <div class="highlight hl-ipython3">'
        content = content + "\n" + '<pre><span></span><span class="kn">import</span> <span class="nn">os</span>'
        content = content + "\n" + '      <span class="kn">import</span> <span class="nn">dotenv</span>'
        content = content + "\n" + '      '
        content = content + "\n" + '      <span class="n">dotenv</span><span class="o">.</span><span class="n">load_dotenv</span><span class="p">()</span>'
        content = content + "\n" + '      '
        content = content + "\n" + '      <span class="n">RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">getenv</span><span class="p">(</span><span class="s2">"RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN"</span><span class="p">)</span>'
        content = content + "\n" + '      </pre></div>'
        content = content + "\n" + '      </div>'
        content = content + "\n" + '      </section>'

        #    <CodeBlockInputCell
        #        text={[
        #    '<span></span><span class="kn">import</span> <span class="nn">os</span>',
        #    '<span class="kn">import</span> <span class="nn">dotenv</span>',
        #    ' ',
        #    '<span class="n">dotenv</span><span class="o">.</span><span class="n">load_dotenv</span><span class="p">()</span>',
        #    ' ',
        #    '<span class="n">RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN</span> <span class="o">=</span> <span class="n">os</span><span class="o">.</span><span class="n">getenv</span><span class="p">(</span><span class="s2">"RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN"</span><span class="p">)</span>',
        #        ]}
        #        languaje='python'
        #    ></CodeBlockInputCell>
        content_formated =                           "      <CodeBlockInputCell"
        content_formated = content_formated + "\n" + "        text={["
        content_formated = content_formated + "\n" + "      '<span></span><span class=\"kn\">import</span> <span class=\"nn\">os</span>',"
        content_formated = content_formated + "\n" + "      '<span class=\"kn\">import</span> <span class=\"nn\">dotenv</span>',"
        content_formated = content_formated + "\n" + "      '',"
        content_formated = content_formated + "\n" + "      '<span class=\"n\">dotenv</span><span class=\"o\">.</span><span class=\"n\">load_dotenv</span><span class=\"p\">()</span>',"
        content_formated = content_formated + "\n" + "      '',"
        content_formated = content_formated + "\n" + "      '<span class=\"n\">RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN</span> <span class=\"o\">=</span> <span class=\"n\">os</span><span class=\"o\">.</span><span class=\"n\">getenv</span><span class=\"p\">(</span><span class=\"s2\">\"RAG_FUNDAMENTALS_ADVANCE_TECHNIQUES_TOKEN\"</span><span class=\"p\">)</span>',"
        content_formated = content_formated + "\n" + "        ]}"
        content_formated = content_formated + "\n" + "        languaje='python'"
        content_formated = content_formated + "\n" + "      ></CodeBlockInputCell>"
        content_formated = content_formated + "\n" + ""
        # print("")
        formated_content = format_code_blocks(content)
        # print(f"\ncontent:\n{content}")
        # print(f"\ncontent_formated:\n{content_formated}")
        # print(f"\nformated_content:\n{formated_content}")
        content_formated_lines = content_formated.split('\n')
        formated_content_lines = formated_content.split('\n')
        # if len(content_formated_lines) != len(formated_content_lines):
        #     print(f"len(content_formated_lines): {len(content_formated_lines)}")
        #     print(f"len(formated_content_lines): {len(formated_content_lines)}")
        for i, line in enumerate(content_formated_lines):
            if line != content_formated_lines[i]:
                self.assertEqual(line, content_formated_lines[i])
        # self.assertEqual(content_formated, formated_content)
        pass

    def test_format_input_code_block_h1(self):
        content = '      <section class="section-block-markdown-cell">\n      <h1 id="Whisper">Whisper<a class="anchor-link" href="#Whisper"><img decoding="async" class="link-img" width="24px" height="24px" alt="link image 0" src={svg_paths.link_svg_path}/></a></h1>\n      </section>\n'
        expected_output = None
        output = format_input_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_input_code_block_h2(self):
        content = '      <section class="section-block-markdown-cell">\n      <h2 id="Instalacion">Instalación<a class="anchor-link" href="#Instalacion"><img decoding="async" class="link-img" width="24px" height="24px" alt="link image 2" src={svg_paths.link_svg_path}/></a></h2>\n      </section>\n'
        expected_output = None
        output = format_input_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_input_code_block_text(self):
        content = '      <section class="section-block-markdown-cell">\n      <p>Para poder instalar esta herramienta lo mejor es crearse un nuevo entorno de Anaconda</p>\n      </section>\n'
        expected_output = None
        output = format_input_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_input_code_block_shell_code_one_line(self):
        content = '      <section class="section-block-code-cell-">\n      <div class="input-code">\n      <div class="highlight hl-ipython3">\n<pre><span></span><span class="err">!</span><span class="n">conda</span> <span class="n">create</span> <span class="o">-</span><span class="n">n</span> <span class="n">whisper</span>\n      </pre></div>\n      </div>\n      </section>\n'
        expected_output = """      <CodeBlockInputCell
        text={[
      '<span></span><span class="err">!</span><span class="n">conda</span> <span class="n">create</span> <span class="o">-</span><span class="n">n</span> <span class="n">whisper</span>',
        ]}
        languaje='python'
      ></CodeBlockInputCell>"""
        output = format_input_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_input_code_block_python_code_one_line(self):
        content = '      <section class="section-block-code-cell-">\n      <div class="input-code">\n      <div class="highlight hl-ipython3">\n<pre><span></span><span class="kn">import</span><span class="w"> </span><span class="nn">whisper</span>\n      </pre></div>\n      </div>\n      </section>\n'
        expected_output = """      <CodeBlockInputCell
        text={[
      '<span></span><span class="kn">import</span><span class="w"> </span><span class="nn">whisper</span>',
        ]}
        languaje='python'
      ></CodeBlockInputCell>"""
        output = format_input_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_input_code_block_python_code_multiple_lines(self):
        content = '      <section class="section-block-code-cell-">\n      <div class="input-code">\n      <div class="highlight hl-ipython3">\n<pre><span></span><span class="c1"># model = &quot;tiny&quot;</span>\n      <span class="c1"># model = &quot;base&quot;</span>\n      <span class="c1"># model = &quot;small&quot;</span>\n      <span class="c1"># model = &quot;medium&quot;</span>\n      <span class="n">model</span> <span class="o">=</span> <span class="s2">&quot;large&quot;</span>\n      <span class="n">model</span> <span class="o">=</span> <span class="n">whisper</span><span class="o">.</span><span class="n">load_model</span><span class="p">(</span><span class="n">model</span><span class="p">)</span>\n      </pre></div>\n      </div>\n      </section>\n'
        expected_output = """      <CodeBlockInputCell
        text={[
      '<span></span><span class="c1"># model = &quot;tiny&quot;</span>',
      '<span class="c1"># model = &quot;base&quot;</span>',
      '<span class="c1"># model = &quot;small&quot;</span>',
      '<span class="c1"># model = &quot;medium&quot;</span>',
      '<span class="n">model</span> <span class="o">=</span> <span class="s2">&quot;large&quot;</span>',
      '<span class="n">model</span> <span class="o">=</span> <span class="n">whisper</span><span class="o">.</span><span class="n">load_model</span><span class="p">(</span><span class="n">model</span><span class="p">)</span>',
        ]}
        languaje='python'
      ></CodeBlockInputCell>"""
        output = format_input_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_output_code_block_h1(self):
        content = '      <section class="section-block-markdown-cell">\n      <h1 id="Whisper">Whisper<a class="anchor-link" href="#Whisper"><img decoding="async" class="link-img" width="24px" height="24px" alt="link image 0" src={svg_paths.link_svg_path}/></a></h1>\n      </section>\n'
        expected_output = None
        output = format_output_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_output_code_block_h2(self):
        content = '      <section class="section-block-markdown-cell">\n      <h2 id="Instalacion">Instalación<a class="anchor-link" href="#Instalacion"><img decoding="async" class="link-img" width="24px" height="24px" alt="link image 2" src={svg_paths.link_svg_path}/></a></h2>\n      </section>\n'
        expected_output = None
        output = format_output_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_output_code_block_text(self):
        content = '      <section class="section-block-markdown-cell">\n      <p>Para poder instalar esta herramienta lo mejor es crearse un nuevo entorno de Anaconda</p>\n      </section>\n'
        expected_output = None
        output = format_output_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_output_code_block_one_line_1(self):
        content = '      <section class="section-block-code-cell-">\n      <div class="output-wrapper">\n      <div class="output-area">\n      <div class="prompt"></div>\n      <div class="output-subarea-output-stream-output-stdout-output-text">\n      <pre>Detected language: en\n      </pre>\n      </div>\n      </div>\n      </div>\n      </section>\n'
        expected_output = """      <CodeBlockOutputCell
        text={[
          'Detected language: en',
        ]}
        languaje='python'
      ></CodeBlockOutputCell>"""
        output = format_output_code_block(content)
        self.assertEqual(output, expected_output)
    
    def test_format_output_code_block_one_line_2(self):
        content = '      <section class="section-block-code-cell-">\n      <div class="output-wrapper">\n      <div class="output-area">\n      <div class="prompt-output-prompt">Out[]:</div>\n      <div class="output-text-output-subareaoutput_execute_result">\n      <pre>&quot;This is the Micro Machine Man presenting the most midget miniature motorcade of micro machines. Each one has dramatic details, terrific trim, precision paint jobs, plus incredible micro machine pocket play sets. There&#x27;s a police station, fire station, restaurant, service station, and more. Perfect pocket portables to take any place. And there are many miniature play sets to play with and each one comes with its own special edition micro machine vehicle and fun fantastic features that miraculously move. Raise the boat lift at the airport, marina, man the gun turret at the army base, clean your car at the car wash, raise the toll bridge. And these play sets fit together to form a micro machine world. Micro machine pocket play sets so tremendously tiny, so perfectly precise, so dazzlingly detailed, you&#x27;ll want to pocket them all. Micro machines and micro machine pocket play sets sold separately from Galoob. The smaller they are, the better they are.&quot;</pre>\n      </div>\n      </div>\n      </div>\n      </section>\n'
        expected_output = """      <CodeBlockOutputCell
        text={[
          '&quot;This is the Micro Machine Man presenting the most midget miniature motorcade of micro machines. Each one has dramatic details, terrific trim, precision paint jobs, plus incredible micro machine pocket play sets. There&#x27;s a police station, fire station, restaurant, service station, and more. Perfect pocket portables to take any place. And there are many miniature play sets to play with and each one comes with its own special edition micro machine vehicle and fun fantastic features that miraculously move. Raise the boat lift at the airport, marina, man the gun turret at the army base, clean your car at the car wash, raise the toll bridge. And these play sets fit together to form a micro machine world. Micro machine pocket play sets so tremendously tiny, so perfectly precise, so dazzlingly detailed, you&#x27;ll want to pocket them all. Micro machines and micro machine pocket play sets sold separately from Galoob. The smaller they are, the better they are.&quot;',
        ]}
        languaje='python'
      ></CodeBlockOutputCell>"""
        output = format_output_code_block(content)
        self.assertEqual(output, expected_output)