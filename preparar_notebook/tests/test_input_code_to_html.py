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

    def test_one_line_split_in_multiple_lines_bash_code(self):
        input_code = "!cd ~/comitizen_folder/.git/hooks &amp;&amp; \\\necho '#!/bin/sh' &gt; commit-msg &amp;&amp; \\\necho '# Este script valida el mensaje del commit usando commitizen' &gt;&gt; commit-msg &amp;&amp; \\\necho ' ' &gt;&gt; commit-msg &amp;&amp; \\\necho 'COMMIT_MSG_FILE=$1' &gt;&gt; commit-msg &amp;&amp; \\\necho 'cz check --commit-msg-file $COMMIT_MSG_FILE' &gt;&gt; commit-msg"
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="err">!</span><span class="n">cd</span> <span class="o">~/</span><span class="n">comitizen_folder</span><span class="o">/.</span><span class="n">git</span><span class="o">/</span><span class="n">hooks</span> <span class="o">&amp;</span></span><span class="o">&amp;</span> \\\\
<span class="n">echo</span> <span class="s1">&#39;#!/bin/sh&#39;</span> <span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span> <span class="n">commit</span><span class="o">-</span><span class="n">msg</span> <span class="o">&amp;</span></span><span class="o">&amp;</span> \\\\
<span class="n">echo</span> <span class="s1">&#39;# Este script valida el mensaje del commit usando commitizen&#39;</span> <span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span><span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span> <span class="n">commit</span><span class="o">-</span><span class="n">msg</span> <span class="o">&amp;</span></span><span class="o">&amp;</span> \\\\
<span class="n">echo</span> <span class="s1">&#39; &#39;</span> <span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span><span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span> <span class="n">commit</span><span class="o">-</span><span class="n">msg</span> <span class="o">&amp;</span></span><span class="o">&amp;</span> \\\\
<span class="n">echo</span> <span class="s1">&#39;COMMIT_MSG_FILE=$1&#39;</span> <span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span><span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span> <span class="n">commit</span><span class="o">-</span><span class="n">msg</span> <span class="o">&amp;</span></span><span class="o">&amp;</span> \\\\
<span class="n">echo</span> <span class="s1">&#39;cz check --commit-msg-file $COMMIT_MSG_FILE&#39;</span> <span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span><span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span> <span class="n">commit</span><span class="o">-</span><span class="n">msg</span>
</pre></div>
</div>
</section>'''
        html = input_code_to_html(input_code)
        self.assertEqual(html, expected_html)

    def test_color_escape_codes(self):
        input_code = '# Colors for the terminal\nCOLOR_GREEN = "\\033[32m"\nCOLOR_YELLOW = "\\033[33m"\nCOLOR_RESET = "\\033[0m"\n\n\ndef stream_graph_updates(user_input: str):\n    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):\n        for value in event.values():\n            print(f"{COLOR_GREEN}User: {COLOR_RESET}{user_input}")\n            print(f"{COLOR_YELLOW}Assistant: {COLOR_RESET}{value[\'messages\'][-1].content}")\n\n\nwhile True:\n    try:\n        user_input = input("User: ")\n        if user_input.lower() in ["quit", "exit", "q"]:\n            print(f"{COLOR_GREEN}User: {COLOR_RESET}{user_input}")\n            print(f"{COLOR_YELLOW}Assistant: {COLOR_RESET}Goodbye!")\n            break\n        \n        events =stream_graph_updates(user_input)\n    except:\n        # fallback if input() is not available\n        user_input = "What do you know about LangGraph?"\n        print("User: " + user_input)\n        stream_graph_updates(user_input)\n        break'
        expected_html = '''<section class="section-block-code-cell-">
<div class="input-code">
<div class="highlight hl-ipython3"><pre><span></span><span class="c1"># Colors for the terminal</span>
<span class="n">COLOR_GREEN</span> <span class="o">=</span> <span class="s2">&quot;</span><span class="se">\\\\033</span><span class="s2">[32m&quot;</span>
<span class="n">COLOR_YELLOW</span> <span class="o">=</span> <span class="s2">&quot;</span><span class="se">\\\\033</span><span class="s2">[33m&quot;</span>
<span class="n">COLOR_RESET</span> <span class="o">=</span> <span class="s2">&quot;</span><span class="se">\\\\033</span><span class="s2">[0m&quot;</span>
<span class="w"> </span>

<span class="k">def</span><span class="w"> </span><span class="nf">stream_graph_updates</span><span class="p">(</span><span class="n">user_input</span><span class="p">:</span> <span class="nb">str</span><span class="p">):</span>
<span class="w">    </span><span class="k">for</span> <span class="n">event</span> <span class="ow">in</span> <span class="n">graph</span><span class="o">.</span><span class="n">stream</span><span class="p">({</span><span class="s2">&quot;messages&quot;</span><span class="p">:</span> <span class="p">[{</span><span class="s2">&quot;role&quot;</span><span class="p">:</span> <span class="s2">&quot;user&quot;</span><span class="p">,</span> <span class="s2">&quot;content&quot;</span><span class="p">:</span> <span class="n">user_input</span><span class="p">}]}):</span>
<span class="w">        </span><span class="k">for</span> <span class="n">value</span> <span class="ow">in</span> <span class="n">event</span><span class="o">.</span><span class="n">values</span><span class="p">():</span>
<span class="w">            </span><span class="nb">print</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">COLOR_GREEN</span><span class="si">}</span><span class="s2">User: </span><span class="si">{</span><span class="n">COLOR_RESET</span><span class="si">}{</span><span class="n">user_input</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
<span class="w">            </span><span class="nb">print</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">COLOR_YELLOW</span><span class="si">}</span><span class="s2">Assistant: </span><span class="si">{</span><span class="n">COLOR_RESET</span><span class="si">}{</span><span class="n">value</span><span class="p">[</span><span class="s1">&#39;messages&#39;</span><span class="p">][</span><span class="o">-</span><span class="mi">1</span><span class="p">]</span><span class="o">.</span><span class="n">content</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
<span class="w"> </span>

<span class="k">while</span> <span class="kc">True</span><span class="p">:</span>
<span class="w">    </span><span class="k">try</span><span class="p">:</span>
<span class="w">        </span><span class="n">user_input</span> <span class="o">=</span> <span class="nb">input</span><span class="p">(</span><span class="s2">&quot;User: &quot;</span><span class="p">)</span>
<span class="w">        </span><span class="k">if</span> <span class="n">user_input</span><span class="o">.</span><span class="n">lower</span><span class="p">()</span> <span class="ow">in</span> <span class="p">[</span><span class="s2">&quot;quit&quot;</span><span class="p">,</span> <span class="s2">&quot;exit&quot;</span><span class="p">,</span> <span class="s2">&quot;q&quot;</span><span class="p">]:</span>
<span class="w">            </span><span class="nb">print</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">COLOR_GREEN</span><span class="si">}</span><span class="s2">User: </span><span class="si">{</span><span class="n">COLOR_RESET</span><span class="si">}{</span><span class="n">user_input</span><span class="si">}</span><span class="s2">&quot;</span><span class="p">)</span>
<span class="w">            </span><span class="nb">print</span><span class="p">(</span><span class="sa">f</span><span class="s2">&quot;</span><span class="si">{</span><span class="n">COLOR_YELLOW</span><span class="si">}</span><span class="s2">Assistant: </span><span class="si">{</span><span class="n">COLOR_RESET</span><span class="si">}</span><span class="s2">Goodbye!&quot;</span><span class="p">)</span>
<span class="w">            </span><span class="k">break</span>
<span class="w">        </span>
<span class="w">        </span><span class="n">events</span> <span class="o">=</span><span class="n">stream_graph_updates</span><span class="p">(</span><span class="n">user_input</span><span class="p">)</span>
<span class="w">    </span><span class="k">except</span><span class="p">:</span>
<span class="w">        </span><span class="c1"># fallback if input() is not available</span>
<span class="w">        </span><span class="n">user_input</span> <span class="o">=</span> <span class="s2">&quot;What do you know about LangGraph?&quot;</span>
<span class="w">        </span><span class="nb">print</span><span class="p">(</span><span class="s2">&quot;User: &quot;</span> <span class="o">+</span> <span class="n">user_input</span><span class="p">)</span>
<span class="w">        </span><span class="n">stream_graph_updates</span><span class="p">(</span><span class="n">user_input</span><span class="p">)</span>
<span class="w">        </span><span class="k">break</span>
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
