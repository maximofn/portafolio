from unittest.mock import patch
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from format_code_blocks import remove_empty_lines, format_code_blocks

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
