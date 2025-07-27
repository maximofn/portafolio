import os
import unittest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.jupyter_notebook_to_html.generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns
from src.jupyter_notebook_to_html.markdown_code_to_html_converter import markdown_code_to_html
from src.jupyter_notebook_to_html.markdown_image_to_html import markdown_image_to_html
from src.jupyter_notebook_to_html.markdown_link_to_html import markdown_to_html_external_link, markdown_to_html_internal_link
from src.jupyter_notebook_to_html.markdown_lists_to_html import markdown_to_html_updated # Using the refined function
from src.jupyter_notebook_to_html.markdown_table_to_html import markdown_table_to_html
from src.jupyter_notebook_to_html.jupyter_notebook_to_html import jupyter_notebook_contents_in_xml_format_to_html

class TestGenericMarkdownToSpecificMarkdowns(unittest.TestCase): # Renamed from TestMarkdownCodeToHtml to avoid conflict
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_text_markdown(self):
        markdown_content = "This is a text markdown"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'text': 'This is a text markdown'}])

    def test_code_markdown1(self):
        markdown_content = "```python\nprint('hello world')\n```"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'code': '```python\nprint(\'hello world\')\n```'}])

    def test_code_markdown2(self):
        markdown_content = '``` bash\nsudo apt update\nsudo apt install fail2ban\n```'
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'code': '```bash\nsudo apt update\nsudo apt install fail2ban\n```'}])

    def test_table_markdown(self):
        markdown_content = "| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |\n| Data 4   | Data 5   | Data 6   |"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'table': '| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |\n| Data 4   | Data 5   | Data 6   |'}])

    def test_list_markdown_guion(self):
        markdown_content = " - Item 1\n - Item 2\n - Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'list': ' - Item 1\n - Item 2\n - Item 3\n'}])

    def test_list_markdown_asterisk(self):
        markdown_content = " * Item 1\n * Item 2\n * Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'list': ' * Item 1\n * Item 2\n * Item 3\n'}])

    def test_list_markdown_plus(self):
        markdown_content = " + Item 1\n + Item 2\n + Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'list': ' + Item 1\n + Item 2\n + Item 3\n'}])

    def test_list_markdown_number(self):
        markdown_content = " 1. Item 1\n 2. Item 2\n 3. Item 3"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'list': ' 1. Item 1\n 2. Item 2\n 3. Item 3\n'}])

    def test_external_url_markdown(self):
        markdown_content = "[Link](https://www.google.com)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'link': '[Link](https://www.google.com)'}])

    def test_internal_es_link_markdown(self):
        markdown_content = "[Link](https://www.maximofn.com/blog)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'link': '[Link](/blog)'}])

    def test_internal_en_link_markdown(self):
        markdown_content = "[Link](https://www.maximofn.com/en/blog/)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'link': '[Link](/en/blog/)'}])

    def test_internal_pt_link_markdown(self):
        markdown_content = "[Link](https://www.maximofn.com/pt-br/blog/)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'link': '[Link](/pt-br/blog/)'}])

    def test_image_markdown(self):
        markdown_content = "![Image](image.png)"
        specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)
        self.assertEqual(specific_markdowns, [{'image': '![Image](image.png)'}])

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
            {'text': 'This is a text markdown'},
            {'code': '```python\nprint(\'hello world\')\n```'},
            {'table': '| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n| Data 1   | Data 2   | Data 3   |\n| Data 4   | Data 5   | Data 6   |\n'},
            {'list': ' - Item 1\n - Item 2\n - Item 3\n'},
            {'list': ' + Item 1\n + Item 2\n + Item 3\n'},
            {'list': ' 1. Item 1\n 2. Item 2\n 3. Item 3\n'},
            {'link': '[Link](https://www.google.com)'},
            {'link': '[Link](/blog)'},
            {'link': '[Link](/en/blog/)'},
            {'link': '[Link](/pt-br/blog/)'},
            {'image': '![Image](image.png)'},
        ]
        self.assertEqual(specific_markdowns, expected_specific_markdowns)

class TestMarkdownCodeToHtml(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello_world_without_space(self):
        markdown_content = "```python\nprint('hello world')\n```"
        html = markdown_code_to_html(markdown_content)
        expected_html = '<div class=\'highlight\'><pre><code>print(&#39;hello world&#39;)\n</code></pre></div>\n'
        self.assertEqual(html, expected_html)

    def test_hello_world_with_space(self):
        markdown_content = "``` python\nprint('hello world')\n```"
        html = markdown_code_to_html(markdown_content)
        expected_html = '<div class=\'highlight\'><pre><code>print(&#39;hello world&#39;)\n</code></pre></div>\n'
        self.assertEqual(html, expected_html)

    def test_two_lines_bash_code(self):
        markdown_content = '```bash\nsudo apt update\nsudo apt install fail2ban\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-bash">sudo apt update<br>sudo apt install fail2ban</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
    
    def test_two_lines_python_code(self):
        markdown_content = '```python\nHUGGINGFACE_TOKEN_INFERENCE_PROVIDERS="hf_aL...AY"\nREPLICATE_API_KEY="r8_Sh...UD"\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-python">HUGGINGFACE_TOKEN_INFERENCE_PROVIDERS="hf_aL...AY"<br>REPLICATE_API_KEY="r8_Sh...UD"</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
      
    def test_code_multiple_lines_python_code(self):
        markdown_content = '```pyhon\n# Monkey patch setup_tunnel para que acepte el parámetro adicional\ndef patched_setup_tunnel(host, port, share_token, share_server_address, share_server_tls_certificate=None):\n    return original_setup_tunnel(host, port, share_token, share_server_address, share_server_tls_certificate)\n\n# Replace the original function with our patched version\ngradio.networking.setup_tunnel = patched_setup_tunnel\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-python"># Monkey patch setup_tunnel para que acepte el parámetro adicional<br>def patched_setup_tunnel(host, port, share_token, share_server_address, share_server_tls_certificate=None):<br>&#x20;&#x20;return original_setup_tunnel(host, port, share_token, share_server_address, share_server_tls_certificate)<br><br># Replace the original function with our patched version<br>gradio.networking.setup_tunnel = patched_setup_tunnel</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
      
    def test_code_git_commit_message(self):
        markdown_content = '```git\n<type>[optional scope]: <description>\n\n[optional body]\n\n[optional footer(s)]\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-git">&lt;type&gt;[optional scope]: &lt;description&gt;<br><br>[optional body]<br><br>[optional footer(s)]</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
    
    def test_code_readme_md(self):
        markdown_content = '```md\n---\ntitle: SmolLM2\nemoji: 💬\ncolorFrom: yellow\ncolorTo: purple\nsdk: gradio\nsdk_version: 5.0.1\napp_file: app.py\npinned: false\nlicense: apache-2.0\nshort_description: Gradio SmolLM2 chat\n---\n\nAn example chatbot using [Gradio](https://gradio.app), [`huggingface_hub`](https://huggingface.co/docs/huggingface_hub/v0.22.2/en/index), and the [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index).\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-md">---<br>title: SmolLM2<br>emoji: 💬<br>colorFrom: yellow<br>colorTo: purple<br>sdk: gradio<br>sdk_version: 5.0.1<br>app_file: app.py<br>pinned: false<br>license: apache-2.0<br>short_description: Gradio SmolLM2 chat<br>---<br><br>An example chatbot using [Gradio](https://gradio.app), [`huggingface_hub`](https://huggingface.co/docs/huggingface_hub/v0.22.2/en/index), and the [Hugging Face Inference API](https://huggingface.co/docs/api-inference/index).</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
    
    def test_code_open_brace(self):
        markdown_content = '```python\n# Define the function that calls the model\ndef call_model(state: MessagesState):\n"""\nLlamar al modelo con los mensajes dados\n\nArgs:\nstate: MessagesState\n\nDevuelve:\ndict: A dictionary containing the generated text and the thread ID\n"""\n# Convert LangChain messages to HuggingFace format\nhf_messages = []\nfor msg in state["messages"]:\nif isinstance(msg, HumanMessage):\nhf_messages.append({"role": "user", "content": msg.content})\nelif isinstance(msg, AIMessage):\nhf_messages.append({"role": "assistant", "content": msg.content})\n    \n# Call the API\nresponse = model.chat_completion(\nmessages=hf_messages,\ntemperature=0.5,\nmax_tokens=64,\ntop_p=0.7\n)\n    \n# Convert the response to LangChain format\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-python"># Define the function that calls the model<br>def call_model(state: MessagesState):<br>"""<br>Llamar al modelo con los mensajes dados<br><br>Args:<br>state: MessagesState<br><br>Devuelve:<br>dict: A dictionary containing the generated text and the thread ID<br>"""<br># Convert LangChain messages to HuggingFace format<br>hf_messages = []<br>for msg in state["messages"]:<br>if isinstance(msg, HumanMessage):<br>hf_messages.append(&#123;"role": "user", "content": msg.content&#125;)<br>elif isinstance(msg, AIMessage):<br>hf_messages.append(&#123;"role": "assistant", "content": msg.content&#125;)<br>    <br># Call the API<br>response = model.chat_completion(<br>messages=hf_messages,<br>temperature=0.5,<br>max_tokens=64,<br>top_p=0.7<br>)<br>    <br># Convert the response to LangChain format</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
    
    def test_code_open_brace_2(self):
        markdown_content = '```python\n# Define the function that calls the model\ndef call_model(state: MessagesState):\n"""\nLlamar al modelo con los mensajes dados\n\nArgs:\nstate: MessagesState\n\nDevuelve:\ndict: A dictionary containing the generated text and the thread ID\n"""\n# Convert LangChain messages to HuggingFace format\nhf_messages = []\nfor msg in state["messages"]:\nif isinstance(msg, HumanMessage):\nhf_messages.append({"role": "user", "content": msg.content})\nelif isinstance(msg, AIMessage):\nhf_messages.append({"role": "assistant", "content": msg.content})\n    \n# Call the API\nresponse = model.chat_completion(\nmessages=hf_messages,\ntemperature=0.5,\nmax_tokens=64,\ntop_p=0.7\n)\n    \n# Convert the response to LangChain format\nai_message = AIMessage(content=response.choices[0].message.content)\nreturn {"messages": state["messages"] + [ai_message]}\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-python"># Define the function that calls the model<br>def call_model(state: MessagesState):<br>"""<br>Llamar al modelo con los mensajes dados<br><br>Args:<br>state: MessagesState<br><br>Devuelve:<br>dict: A dictionary containing the generated text and the thread ID<br>"""<br># Convert LangChain messages to HuggingFace format<br>hf_messages = []<br>for msg in state["messages"]:<br>if isinstance(msg, HumanMessage):<br>hf_messages.append(&#123;"role": "user", "content": msg.content&#125;)<br>elif isinstance(msg, AIMessage):<br>hf_messages.append(&#123;"role": "assistant", "content": msg.content&#125;)<br>    <br># Call the API<br>response = model.chat_completion(<br>messages=hf_messages,<br>temperature=0.5,<br>max_tokens=64,<br>top_p=0.7<br>)<br>    <br># Convert the response to LangChain format<br>ai_message = AIMessage(content=response.choices[0].message.content)<br>return &#123;"messages": state["messages"] + [ai_message]&#125;</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)
    
    def test_code_open_brace_3(self):
        markdown_content = '```c\nfor (i = 0; i < rows; i++): {\n  for (j = 0; j < columns; j++): {\n    c[i][j] = a[i][j]*b[i][j];\n  }\n}\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-c">for (i = 0; i &lt; rows; i++): &#123;<br>  for (j = 0; j &lt; columns; j++): &#123;<br>    c[i][j] = a[i][j]*b[i][j];<br>  &#125;<br>&#125;</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)

    def test_code_greater_than_sign_in_html(self):
        markdown_content = '```html\n<div>\n    <p>Texto</p>\n</div>\n```'
        html = markdown_code_to_html(markdown_content)
        expected_html = '''<section class="section-block-markdown-cell">
      <div class='highlight'><pre><code class="language-html">&lt;div&gt;<br>&#x20;&#x20;&lt;p&gt;Texto&lt;/p&gt;<br>&lt;/div&gt;</code></pre></div>
      </section>'''
        self.assertEqual(html, expected_html)

class TestMarkdownImageToHtml(unittest.TestCase):

    def test_valid_markdown_image(self):
        markdown = "![alt text](image.png)"
        expected_html = '<img src="image.png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_url_and_alt_text_in_sentence(self):
        markdown = "An image ![alt text for image](http://example.com/img.jpg) in a sentence."
        expected_html = 'An image <img src="http://example.com/img.jpg" alt="alt text for image"> in a sentence.'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_empty_alt_text(self):
        markdown = "![](image_no_alt.gif)"
        expected_html = '<img src="image_no_alt.gif" alt="">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_spaces_in_url(self):
        markdown = "![alt text](my image path.png)"
        expected_html = '<img src="my image path.png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_multiple_images_in_one_line(self):
        markdown = "![alt1](url1.png) and ![alt2](url2.jpg)"
        expected_html = '<img src="url1.png" alt="alt1"> and <img src="url2.jpg" alt="alt2">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_no_markdown_image_present(self):
        markdown = "This is a regular text without any image."
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_empty_string_input(self):
        markdown = ""
        self.assertEqual(markdown_image_to_html(markdown), "")

    def test_markdown_image_missing_url(self):
        markdown = "![alt text]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_malformed_markdown_no_closing_parenthesis_for_url(self):
        markdown = "![alt text](image.png"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_malformed_markdown_no_closing_bracket_for_alt_text(self):
        markdown = "![alt text(image.png)"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_text_that_looks_like_image_but_is_not_markdown_link(self):
        markdown = "This is not an image: [alt text](image.png)"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_image_at_start_of_string(self):
        markdown = "![alt text](image.png) Some following text."
        expected_html = '<img src="image.png" alt="alt text"> Some following text.'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_at_end_of_string(self):
        markdown = "Some preceding text. ![alt text](image.png)"
        expected_html = 'Some preceding text. <img src="image.png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_relative_path(self):
        markdown = "![logo](../images/logo.svg)"
        expected_html = '<img src="../images/logo.svg" alt="logo">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_with_query_parameters_in_url(self):
        markdown = "![tracking pixel](pixel.gif?id=123&user=abc)"
        expected_html = '<img src="pixel.gif?id=123&user=abc" alt="tracking pixel">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_inside_a_link_like_construct_but_still_image(self):
        markdown = "[![alt text](image.png)](destination_url)"
        expected_html = '[<img src="image.png" alt="alt text">](destination_url)'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_only_exclamation_and_brackets_no_parentheses(self):
        markdown = "![alt text]"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_exclamation_brackets_empty_parentheses(self):
        markdown = "![alt text]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_no_alt_text_no_url(self):
        markdown = "![]()"
        self.assertEqual(markdown_image_to_html(markdown), markdown)

    def test_alt_text_contains_brackets(self):
        markdown = "![alt [text] here](image.png)"
        expected_html = '<img src="image.png" alt="alt [text] here">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_url_contains_parentheses_not_supported_by_simple_regex(self):
        markdown = "![alt text](http://example.com/path(with_parens).png)"
        expected_html = '<img src="http://example.com/path(with_parens).png" alt="alt text">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

    def test_image_gif(self):
        markdown = '![Transformer - encoder-decoder (no detokenizer)](https://pub-fb664c455eca46a2ba762a065ac900f7.r2.dev/Transformer%20-%20encoder-decoder%20(no%20detokenizer).gif)'
        expected_html = '<img src="https://pub-fb664c455eca46a2ba762a065ac900f7.r2.dev/Transformer%20-%20encoder-decoder%20(no%20detokenizer).gif" alt="Transformer - encoder-decoder (no detokenizer)">'
        self.assertEqual(markdown_image_to_html(markdown), expected_html)

class TestMarkdownLinkToHtml(unittest.TestCase):

    def test_markdown_to_html_external_link(self):
        self.assertEqual(
            markdown_to_html_external_link("[Google](https://google.com)"),
            '<a href="https://google.com">Google</a>'
        )
        self.assertEqual(
            markdown_to_html_external_link("[Example Site](http://example.com)"),
            '<a href="http://example.com">Example Site</a>'
        )
        self.assertEqual(
            markdown_to_html_external_link("[No Protocol](google.com)"),
            "[No Protocol](google.com)"
        )
        self.assertEqual(
            markdown_to_html_external_link("Not a link"),
            "Not a link"
        )
        self.assertEqual(
            markdown_to_html_external_link("[Missing URL]()"),
            "[Missing URL]()"
        )
        self.assertEqual(
            markdown_to_html_external_link("[](https://example.com)"),
            '<a href="https://example.com"></a>'
        )

    def test_markdown_to_html_internal_link(self):
        self.assertEqual(
            markdown_to_html_internal_link("[Homepage](/home)"),
            '<a href="/home">Homepage</a>'
        )
        self.assertEqual(
            markdown_to_html_internal_link("[About Us](/about-us)"),
            '<a href="/about-us">About Us</a>'
        )
        self.assertEqual(
            markdown_to_html_internal_link("[Docs](/docs/api)"),
            '<a href="/docs/api">Docs</a>'
        )
        self.assertEqual(
            markdown_to_html_internal_link("[Google](https://google.com)"),
            "[Google](https://google.com)"
        )
        self.assertEqual(
            markdown_to_html_internal_link("Not a link"),
            "Not a link"
        )
        self.assertEqual(
            markdown_to_html_internal_link("[Missing URL]()"),
            "[Missing URL]()"
        )
        self.assertEqual(
            markdown_to_html_internal_link("[](/internal-page)"),
            '<a href="/internal-page"></a>'
        )

class TestMarkdownUnorderedListToHtml(unittest.TestCase):

    def test_simple_list_hyphen(self):
        markdown = "- item 1\n- item 2\n- item 3"
        expected_html = "<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n  <li>item 3</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_simple_list_asterisk(self):
        markdown = "* item A\n* item B"
        expected_html = "<ul>\n  <li>item A</li>\n  <li>item B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_simple_list_plus(self):
        markdown = "+ entry 1\n+ entry 2"
        expected_html = "<ul>\n  <li>entry 1</li>\n  <li>entry 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_mixed_markers_simple_list(self):
        markdown = "- item 1\n* item 2\n+ item 3"
        expected_html = "<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n  <li>item 3</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_list_hyphen(self):
        markdown = "- level 1 item 1\n  - level 2 item 1\n  - level 2 item 2\n- level 1 item 2"
        expected_html = "<ul>\n  <li>level 1 item 1</li>\n  <ul>\n    <li>level 2 item 1</li>\n    <li>level 2 item 2</li>\n  </ul>\n  <li>level 1 item 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_list_asterisk(self):
        markdown = "* level 1 item A\n  * level 2 item A\n* level 1 item B"
        expected_html = "<ul>\n  <li>level 1 item A</li>\n  <ul>\n    <li>level 2 item A</li>\n  </ul>\n  <li>level 1 item B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_deeply_nested_list(self):
        markdown = "- L1\n  - L2\n    - L3\n      - L4\n- L1B"
        expected_html = "<ul>\n  <li>L1</li>\n  <ul>\n    <li>L2</li>\n    <ul>\n      <li>L3</li>\n      <ul>\n        <li>L4</li>\n      </ul>\n    </ul>\n  </ul>\n  <li>L1B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_list_mixed_markers(self):
        markdown = "- First level item\n  * Second level item\n    + Third level item\n- Another first level item"
        expected_html = "<ul>\n  <li>First level item</li>\n  <ul>\n    <li>Second level item</li>\n    <ul>\n      <li>Third level item</li>\n    </ul>\n  </ul>\n  <li>Another first level item</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_with_varied_indentation_and_markers(self):
        markdown = (
            "* Root A\n"
            "  - Child A1\n"
            "  - Child A2\n"
            "    + Grandchild A2a\n"
            "* Root B\n"
            "  - Child B1"
        )
        expected_html = (
            "<ul>\n"
            "  <li>Root A</li>\n"
            "  <ul>\n"
            "    <li>Child A1</li>\n"
            "    <li>Child A2</li>\n"
            "    <ul>\n"
            "      <li>Grandchild A2a</li>\n"
            "    </ul>\n"
            "  </ul>\n"
            "  <li>Root B</li>\n"
            "  <ul>\n"
            "    <li>Child B1</li>\n"
            "  </ul>\n"
            "</ul>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_empty_input(self):
        markdown = ""
        expected_html = ""
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_input_with_only_whitespace(self):
        markdown = "   \n  \n "
        expected_html = ""
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_input_not_a_list(self):
        markdown = "This is a paragraph."
        expected_html = "<p>This is a paragraph.</p>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_with_surrounding_text(self):
        markdown = "Intro text\n- item 1\n- item 2\nOutro text"
        expected_html = "<p>Intro text</p>\n<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n</ul>\n<p>Outro text</p>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_items_with_leading_trailing_spaces(self):
        markdown = "-   item 1 with spaces  \n- item 2  "
        expected_html = "<ul>\n  <li>item 1 with spaces</li>\n  <li>item 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_incorrect_indentation_resets_list(self):
        markdown = (
            "- Level 1\n"
            "  - Level 2\n"
            "    - Level 3\n"
            " - Incorrectly indented Level 1 (should be new list or error, current logic makes it a new L0 list)"
        )
        expected_html = (
            "<ul>\n"
            "  <li>Level 1</li>\n"
            "  <ul>\n"
            "    <li>Level 2</li>\n"
            "    <ul>\n"
            "      <li>Level 3</li>\n"
            "    </ul>\n"
            "  </ul>\n"
            "  <li>Incorrectly indented Level 1 (should be new list or error, current logic makes it a new L0 list)</li>\n"
            "</ul>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_ending_with_nested_item(self):
        markdown = "- item 1\n  - item 1.1"
        expected_html = "<ul>\n  <li>item 1</li>\n  <ul>\n    <li>item 1.1</li>\n  </ul>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_with_blank_lines_between_items(self):
        markdown = "- item 1\n\n- item 2"
        expected_html = "<ul>\n  <li>item 1</li>\n  <li>item 2</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_starts_with_indentation(self):
        markdown = "  - indented item"
        expected_html = "<ul>\n  <li>indented item</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown).strip(), expected_html.strip())
    
    def test_list_with_links(self):
        markdown = ' * [LLM.int8()](/llm-int8)\n * [GPTQ](/gptq)\n * [QLoRA](/qlora)\n * AWQ\n * QuIP\n * GGUF\n * HQQ\n * AQLM\n * FBGEMM FP8\n'
        expected_html = '<ul>\n  <li><a href="/llm-int8">LLM.int8()</a></li>\n  <li><a href="/gptq">GPTQ</a></li>\n  <li><a href="/qlora">QLoRA</a></li>\n  <li>AWQ</li>\n  <li>QuIP</li>\n  <li>GGUF</li>\n  <li>HQQ</li>\n  <li>AQLM</li>\n  <li>FBGEMM FP8</li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_list_with_strong_text(self):
        markdown = '* **fix**: Se utiliza para corrección de bugs.\n* **feat**: Se utiliza para nuevas funcionalidades.\n * **docs**: Se utiliza para cambios en la documentación.\n* **style**: Se utiliza para cambios que no afectan el significado del código (por ejemplo, formato, eliminación de espacios en blanco).\n * **refactor**: Se utiliza para cambios de código que ni mejoran ni empeoran la funcionalidad, como reorganizar el código.\n * **perf**: Se utiliza para cambios que mejoran el rendimiento.\n* **test**: Se utiliza para agregar o actualizar pruebas.\n * **chore**: Se utiliza para cambios en el proceso o en las herramientas de desarrollo.\n* **ci**: Se utiliza para cambios en los archivos de configuración de integración continua.\n * **build**: Se utiliza para cambios que afectan el sistema de compilación o dependencias externas.\n * **revert**: Se utiliza para revertir un commit anterior.\n'
        expected_html = '<ul>\n  <li><strong>fix</strong>: Se utiliza para corrección de bugs.</li>\n  <li><strong>feat</strong>: Se utiliza para nuevas funcionalidades.</li>\n  <li><strong>docs</strong>: Se utiliza para cambios en la documentación.</li>\n  <li><strong>style</strong>: Se utiliza para cambios que no afectan el significado del código (por ejemplo, formato, eliminación de espacios en blanco).</li>\n  <li><strong>refactor</strong>: Se utiliza para cambios de código que ni mejoran ni empeoran la funcionalidad, como reorganizar el código.</li>\n  <li><strong>perf</strong>: Se utiliza para cambios que mejoran el rendimiento.</li>\n  <li><strong>test</strong>: Se utiliza para agregar o actualizar pruebas.</li>\n  <li><strong>chore</strong>: Se utiliza para cambios en el proceso o en las herramientas de desarrollo.</li>\n  <li><strong>ci</strong>: Se utiliza para cambios en los archivos de configuración de integración continua.</li>\n  <li><strong>build</strong>: Se utiliza para cambios que afectan el sistema de compilación o dependencias externas.</li>\n  <li><strong>revert</strong>: Se utiliza para revertir un commit anterior.</li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_list_with_open_brace(self):
        markdown = '* Primero, lo que hacemos es calcular la salida que obtenemos con nuestro valor actual de pesos $W$, es decir, obtenemos el valor $y$\n* A continuación calculamos el error que existe entre el valor de $y$ que hemos obtenido y el valor que queríamos obtener $\\hat{y}$. A ese error lo llamamos $loss$, y lo calculamos con alguna función matemática, ahora no importa cual\n* Calculamos el gradiente (la derivada) del error $loss$ con respecto a la matriz de pesos $W$, es decir $\\Delta W = \\frac{dloss}{dW}$\n * Actualizamos los pesos $W$ restando a cada uno de sus valores el valor del gradiente multiplicado por un factor de aprendizaje $\\alpha$, es decir $W = W - \\alpha \\Delta W$\n'
        expected_html = '<ul>\n  <li>Primero, lo que hacemos es calcular la salida que obtenemos con nuestro valor actual de pesos <span class="math-inline">W</span>, es decir, obtenemos el valor <span class="math-inline">y</span></li>\n  <li>A continuación calculamos el error que existe entre el valor de <span class="math-inline">y</span> que hemos obtenido y el valor que queríamos obtener <span class="math-inline">\\hat&#123;y&#125;</span>. A ese error lo llamamos <span class="math-inline">loss</span>, y lo calculamos con alguna función matemática, ahora no importa cual</li>\n  <li>Calculamos el gradiente (la derivada) del error <span class="math-inline">loss</span> con respecto a la matriz de pesos <span class="math-inline">W</span>, es decir <span class="math-inline">\\Delta W = \\frac&#123;dloss&#125;&#123;dW&#125;</span></li>\n  <li>Actualizamos los pesos <span class="math-inline">W</span> restando a cada uno de sus valores el valor del gradiente multiplicado por un factor de aprendizaje <span class="math-inline">\\alpha</span>, es decir <span class="math-inline">W = W - \\alpha \\Delta W</span></li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_markdown_to_html_brace_into_code(self):
        markdown = ' * Podemos remplazar el valor de una cadena de un argumento mediante `${<indice de argumento>/cadena que se quiere sustituir/cadena nueva}`, es decir, si tenemos `${1/hola/hello}` sustituirá la palabra `hola` por la palabra `hello` en el argumento 1\n * Sin embargo, si usamos `${<índice de argumento>/#cadena que se quiere sustituir/cadena nueva}`, solo sustituirá la cadena en el argumento si este argumento empieza por dicha cadena\n'
        expected_html = '<ul>\n  <li>Podemos remplazar el valor de una cadena de un argumento mediante <code>$&#123;<indice de argumento>/cadena que se quiere sustituir/cadena nueva&#125;</code>, es decir, si tenemos <code>$&#123;1/hola/hello&#125;</code> sustituirá la palabra <code>hola</code> por la palabra <code>hello</code> en el argumento 1</li>\n  <li>Sin embargo, si usamos <code>$&#123;<índice de argumento>/#cadena que se quiere sustituir/cadena nueva&#125;</code>, solo sustituirá la cadena en el argumento si este argumento empieza por dicha cadena</li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_markdown_to_html_brace_into_code_2(self):
        markdown = '* `{{ if .System }}`system`{{ .System }}``{{ end }}`:\n'
        expected_html = '<ul>\n  <li><code>&#123;&#123; if .System &#125;&#125;</code>system<code>&#123;&#123; .System &#125;&#125;</code><code>&#123;&#123; end &#125;&#125;</code>:</li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_markdown_to_html_grather_than_sign_into_code(self):
        markdown = '- **Selector de clase**: Selecciona todos los elementos que tengan una clase. Se utiliza el nombre de la clase. Por ejemplo, `.clase` selecciona todos los elementos que tengan la clase `clase`. Esto es útil, porque si queremos que todos los botones sean iguales, en el HTML ponemos `<button class="boton">` y en el CSS ponemos `.boton { /* estilos */ }`. Así todos los botones tendrán los mismos estilos, y si queremos que un botón sea diferente, le ponemos otra clase.'
        expected_html = '<ul>\n  <li><strong>Selector de clase</strong>: Selecciona todos los elementos que tengan una clase. Se utiliza el nombre de la clase. Por ejemplo, <code>.clase</code> selecciona todos los elementos que tengan la clase <code>clase</code>. Esto es útil, porque si queremos que todos los botones sean iguales, en el HTML ponemos <code>&lt;button class="boton"&gt;</code> y en el CSS ponemos <code>.boton &#123; /* estilos */ &#125;</code>. Así todos los botones tendrán los mismos estilos, y si queremos que un botón sea diferente, le ponemos otra clase.</li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_markdown_to_html_greater_than_sign_in_list(self):
        markdown = '<li>Sincronizarlos mediante <code>git remote add origin <URL></code></li>'
        expected_html = '<ul>\n  <li>Sincronizarlos mediante <code>git remote add origin &lt;URL&gt;</code></li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_markdown_to_html_greater_than_sign_in_list_2(self):
        markdown = ' * Primero crear un repositorio remoto vacío, en mi caso he creado el repositorio `notebook_git` en GitHub que más tarde borraré\n * Obtener la URL del repositorio o dirección SSH\n * Sincronizarlos mediante `git remote add origin <URL>`\n'
        expected_html = '<ul>\n  <li>Primero crear un repositorio remoto vacío, en mi caso he creado el repositorio <code>notebook_git</code> en GitHub que más tarde borraré</li>\n  <li>Obtener la URL del repositorio o dirección SSH</li>\n  <li>Sincronizarlos mediante <code>git remote add origin &lt;URL&gt;</code></li>\n</ul>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

class TestMarkdownOrderedListToHtml(unittest.TestCase):

    def test_simple_ordered_list(self):
        markdown = "1. Item 1\n2. Item 2\n3. Item 3"
        expected_html = "<ol>\n  <li>Item 1</li>\n  <li>Item 2</li>\n  <li>Item 3</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_with_different_starting_number(self):
        markdown = "3. Item A\n4. Item B"
        expected_html = "<ol>\n  <li>Item A</li>\n  <li>Item B</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_with_non_sequential_numbers(self):
        markdown = "1. First\n3. Third\n2. Second"
        expected_html = "<ol>\n  <li>First</li>\n  <li>Third</li>\n  <li>Second</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_nested_ordered_list(self):
        markdown = "1. Level 1 Item 1\n  1. Level 2 Item 1\n  2. Level 2 Item 2\n2. Level 1 Item 2"
        expected_html = "<ol>\n  <li>Level 1 Item 1</li>\n  <ol>\n    <li>Level 2 Item 1</li>\n    <li>Level 2 Item 2</li>\n  </ol>\n  <li>Level 1 Item 2</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_deeply_nested_ordered_list(self):
        markdown = "1. L1\n  1. L2\n    1. L3\n      1. L4\n2. L1B"
        expected_html = "<ol>\n  <li>L1</li>\n  <ol>\n    <li>L2</li>\n    <ol>\n      <li>L3</li>\n      <ol>\n        <li>L4</li>\n      </ol>\n    </ol>\n  </ol>\n  <li>L1B</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_ending_with_nested_item(self):
        markdown = "1. item 1\n  1. item 1.1"
        expected_html = "<ol>\n  <li>item 1</li>\n  <ol>\n    <li>item 1.1</li>\n  </ol>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_with_leading_trailing_spaces_in_items(self):
        markdown = "1.   item 1 with spaces  \n2. item 2  "
        expected_html = "<ol>\n  <li>item 1 with spaces</li>\n  <li>item 2</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_ordered_list_starts_with_indentation(self):
        markdown = "  1. indented item"
        expected_html = "<ol>\n  <li>indented item</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown).strip(), expected_html.strip())
      
    def test_ordered_list_with_inline_code(self):
        markdown = ' 1. `Flash Attention`: Esta es una implementación de la `attention` que utiliza `sparse` para reducir la complejidad computacional. La atención es una de las operaciones más costosas en los modelos de transformers, y `Flash Attention` la hace más eficiente.\n 2. `Memory-Efficient Attention`: Esta es otra implementación de la atención que utiliza la función `scaled_dot_product_attention` de PyTorch. Esta función es más eficiente en términos de memoria que la implementación estándar de la atención en PyTorch.\n'
        expected_html = '<ol>\n  <li><code>Flash Attention</code>: Esta es una implementación de la <code>attention</code> que utiliza <code>sparse</code> para reducir la complejidad computacional. La atención es una de las operaciones más costosas en los modelos de transformers, y <code>Flash Attention</code> la hace más eficiente.</li>\n  <li><code>Memory-Efficient Attention</code>: Esta es otra implementación de la atención que utiliza la función <code>scaled_dot_product_attention</code> de PyTorch. Esta función es más eficiente en términos de memoria que la implementación estándar de la atención en PyTorch.</li>\n</ol>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)
    
    def test_ordered_list_with_inline_code_with_two_apostrophes(self):
        markdown = '1. ``OpenAI`` y ``Google`` lanzaron sus APIs multimodales en vivo para ChatGPT y Gemini. ¡OpenAI incluso lanzó un número de teléfono ``1-800-ChatGPT``!\n2. ``Kyutai`` lanzó [Moshi](https://huggingface.co/kyutai), un LLM de audio a audio completamente de código abierto.\n3. ``Alibaba`` lanzó [Qwen2-Audio](https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct), un LLM de código abierto que entiende audio de forma nativa.\n4. ``Fixie.ai`` lanzó [Ultravox](https://huggingface.co/fixie-ai/ultravox-v0_5-llama-3_3-70b), otro LLM de código abierto que también entiende audio de forma nativa.\n5. ``ElevenLabs`` recaudó 180 millones de dólares en su Serie C.\n'
        expected_html = '<ol>\n  <li><code>OpenAI</code> y <code>Google</code> lanzaron sus APIs multimodales en vivo para ChatGPT y Gemini. ¡OpenAI incluso lanzó un número de teléfono <code>1-800-ChatGPT</code>!</li>\n  <li><code>Kyutai</code> lanzó <a href="https://huggingface.co/kyutai">Moshi</a>, un LLM de audio a audio completamente de código abierto.</li>\n  <li><code>Alibaba</code> lanzó <a href="https://huggingface.co/Qwen/Qwen2-Audio-7B-Instruct">Qwen2-Audio</a>, un LLM de código abierto que entiende audio de forma nativa.</li>\n  <li><code>Fixie.ai</code> lanzó <a href="https://huggingface.co/fixie-ai/ultravox-v0_5-llama-3_3-70b">Ultravox</a>, otro LLM de código abierto que también entiende audio de forma nativa.</li>\n  <li><code>ElevenLabs</code> recaudó 180 millones de dólares en su Serie C.</li>\n</ol>'
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

class TestMixedMarkdownListsToHtml(unittest.TestCase):

    def test_mixed_list_simple(self):
        markdown = "- Unordered 1\n1. Ordered 1\n- Unordered 2\n2. Ordered 2"
        expected_html = "<ul>\n  <li>Unordered 1</li>\n</ul>\n<ol>\n  <li>Ordered 1</li>\n</ol>\n<ul>\n  <li>Unordered 2</li>\n</ul>\n<ol>\n  <li>Ordered 2</li>\n</ol>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_mixed_list_with_nesting(self):
        markdown = (
            "1. Ordered L1 A\n"
            "  - Unordered L2 A.1\n"
            "  - Unordered L2 A.2\n"
            "2. Ordered L1 B\n"
            "  1. Ordered L2 B.1\n"
            "    * Unordered L3 B.1.a\n"
            "  2. Ordered L2 B.2"
        )
        expected_html = (
            "<ol>\n"
            "  <li>Ordered L1 A</li>\n"
            "  <ul>\n"
            "    <li>Unordered L2 A.1</li>\n"
            "    <li>Unordered L2 A.2</li>\n"
            "  </ul>\n"
            "  <li>Ordered L1 B</li>\n"
            "  <ol>\n"
            "    <li>Ordered L2 B.1</li>\n"
            "    <ul>\n"
            "      <li>Unordered L3 B.1.a</li>\n"
            "    </ul>\n"
            "    <li>Ordered L2 B.2</li>\n"
            "  </ol>\n"
            "</ol>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_list_interspersed_with_text(self):
        markdown = "Paragraph 1.\n\n1. Item 1\n2. Item 2\n\nAnother paragraph.\n\n- Unordered A\n- Unordered B"
        expected_html = "<p>Paragraph 1.</p>\n<ol>\n  <li>Item 1</li>\n  <li>Item 2</li>\n</ol>\n<p>Another paragraph.</p>\n<ul>\n  <li>Unordered A</li>\n  <li>Unordered B</li>\n</ul>"
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

    def test_complex_nesting_and_switching(self):
        markdown = (
            "- U1\n"
            "  1. O2_A\n"
            "    - U3_A1\n"
            "    - U3_A2\n"
            "  2. O2_B\n"
            "- U1_Next\n"
            "1. O1_Separate"
        )
        expected_html = (
            "<ul>\n"
            "  <li>U1</li>\n"
            "  <ol>\n"
            "    <li>O2_A</li>\n"
            "    <ul>\n"
            "      <li>U3_A1</li>\n"
            "      <li>U3_A2</li>\n"
            "    </ul>\n"
            "    <li>O2_B</li>\n"
            "  </ol>\n"
            "  <li>U1_Next</li>\n"
            "</ul>\n"
            "<ol>\n"
            "  <li>O1_Separate</li>\n"
            "</ol>"
        )
        self.assertEqual(markdown_to_html_updated(markdown), expected_html)

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

    def test_table_with_inline_code(self):
        markdown = '|Accelerator\t|Installation|\n|---|---|\n|ONNX Runtime\t|`pip install --upgrade --upgrade-strategy eager optimum[onnxruntime]`|\n|Intel Neural Compressor\t|`pip install --upgrade --upgrade-strategy eager optimum[neural-compressor]`|\n|OpenVINO\t|`pip install --upgrade --upgrade-strategy eager optimum[openvino]`|\n|NVIDIA TensorRT-LLM\t|`docker run -it --gpus all --ipc host huggingface/optimum-nvidia`|\n|AMD Instinct GPUs and Ryzen AI NPU\t|`pip install --upgrade --upgrade-strategy eager optimum[amd]`|\n|AWS Trainum & Inferentia\t|`pip install --upgrade --upgrade-strategy eager optimum[neuronx]`|\n|Habana Gaudi Processor (HPU)\t|`pip install --upgrade --upgrade-strategy eager optimum[habana]`|\n|FuriosaAI\t|`pip install --upgrade --upgrade-strategy eager optimum[furiosa]`|\n'
        expected_html = '''<table>
  <thead>
    <tr>
      <th>Accelerator</th>
      <th>Installation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>ONNX Runtime</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[onnxruntime]</code></td>
    </tr>
    <tr>
      <td>Intel Neural Compressor</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[neural-compressor]</code></td>
    </tr>
    <tr>
      <td>OpenVINO</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[openvino]</code></td>
    </tr>
    <tr>
      <td>NVIDIA TensorRT-LLM</td>
      <td><code>docker run -it --gpus all --ipc host huggingface/optimum-nvidia</code></td>
    </tr>
    <tr>
      <td>AMD Instinct GPUs and Ryzen AI NPU</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[amd]</code></td>
    </tr>
    <tr>
      <td>AWS Trainum & Inferentia</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[neuronx]</code></td>
    </tr>
    <tr>
      <td>Habana Gaudi Processor (HPU)</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[habana]</code></td>
    </tr>
    <tr>
      <td>FuriosaAI</td>
      <td><code>pip install --upgrade --upgrade-strategy eager optimum[furiosa]</code></td>
    </tr>
  </tbody>
</table>'''
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
        markdown = """
| H1 | H2 | H3 |
| -- | -- |
| D1 | D2 | D3 |
"""
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

    def test_empty_input_table(self): # Renamed to avoid conflict
        self.assertEqual(markdown_table_to_html(""), "")

    def test_only_header_table(self): # Renamed to avoid conflict
        markdown = "| H1 | H2 |"
        self.assertEqual(markdown_table_to_html(markdown), "")

    def test_header_and_malformed_separator_table(self): # Renamed to avoid conflict
        markdown = """
| H1 | H2 |
| --xx-- | --yy-- |
"""
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

    def test_markdown_table_to_html_with_less_than_greater_than(self):
        markdown = '| Comando | Velocidad |\n|--------------------|-----------------------|\n| `conda install <pkg>`              | lento           |\n| `pip install <pkg>`             | entre 2 y 10 veces más rápido que el anterior            |\n| `uv pip install <pkg>`                 | entre 5 y 10 veces más rápido que el anterior            |\n| `uv add <pkg>`                 | entre 2 y 5 veces más rápido que el anterior            |'
        expected_html = '''<table>
  <thead>
    <tr>
      <th>Comando</th>
      <th>Velocidad</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>conda install &#x3C;pkg&#x3E;</code></td>
      <td>lento</td>
    </tr>
    <tr>
      <td><code>pip install &#x3C;pkg&#x3E;</code></td>
      <td>entre 2 y 10 veces más rápido que el anterior</td>
    </tr>
    <tr>
      <td><code>uv pip install &#x3C;pkg&#x3E;</code></td>
      <td>entre 5 y 10 veces más rápido que el anterior</td>
    </tr>
    <tr>
      <td><code>uv add &#x3C;pkg&#x3E;</code></td>
      <td>entre 2 y 5 veces más rápido que el anterior</td>
    </tr>
  </tbody>
</table>'''
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_table_to_html_with_code_inline(self):
        markdown = '|Normalización|Descripción|Ejemplo|\n|---|---|---|\n|NFD (Normalization for D)|Los caracteres se descomponen por equivalencia canónica|`â` (U+00E2) se descompone en `a` (U+0061) + `^` (U+0302)|\n|NFKD (Normalization Form KD)|Los caracteres se descomponen por compatibilidad|`ﬁ` (U+FB01) se descompone en `f` (U+0066) + `i` (U+0069)|\n|NFC (Normalization Form C)|Los caracteres se descomponen y luego se recomponen por equivalencia canónica|`â` (U+00E2) se descompone en `a` (U+0061) + `^` (U+0302) y luego se recompone en `â` (U+00E2)|\n|NFKC (Normalization Form KC)|Los caracteres se descomponen por compatibilidad y luego se recomponen por equivalencia canónica|`ﬁ` (U+FB01) se descompone en `f` (U+0066) + `i` (U+0069) y luego se recompone en `f` (U+0066) + `i` (U+0069)|\n|Lowercase|Convierte el texto a minúsculas|`Hello World` se convierte en `hello world`|\n|Strip|Elimina todos los espacios en blanco de los lados especificados (izquierdo, derecho o ambos) del texto|`  Hello World  ` se convierte en `Hello World`|\n|StripAccents|Elimina todos los símbolos de acento en unicode (se utilizará con NFD por coherencia)|`á` (U+00E1) se convierte en `a` (U+0061)|\n|Replace|Sustituye una cadena personalizada o [regex](https://maximofn.com/regular-expressions/) y la cambia por el contenido dado|`Hello World` se convierte en `Hello Universe`|\n|BertNormalizer|Proporciona una implementación del Normalizador utilizado en el BERT original. Las opciones que se pueden configurar son `clean_text`, `handle_chinese_chars`, `strip_accents` y `lowercase`|`Hello World` se convierte en `hello world`|'
        expected_html = '''<table>
  <thead>
    <tr>
      <th>Normalización</th>
      <th>Descripción</th>
      <th>Ejemplo</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>NFD (Normalization for D)</td>
      <td>Los caracteres se descomponen por equivalencia canónica</td>
      <td><code>&#x60;â&#x60;</code> (U+00E2) se descompone en <code>a</code> (U+0061) + <code>^</code> (U+0302)</td>
    </tr>
    <tr>
      <td>NFKD (Normalization Form KD)</td>
      <td>Los caracteres se descomponen por compatibilidad</td>
      <td><code>&#x60;ﬁ&#x60;</code> (U+FB01) se descompone en <code>f</code> (U+0066) + <code>i</code> (U+0069)</td>
    </tr>
    <tr>
      <td>NFC (Normalization Form C)</td>
      <td>Los caracteres se descomponen y luego se recomponen por equivalencia canónica</td>
      <td><code>&#x60;â&#x60;</code> (U+00E2) se descompone en <code>a</code> (U+0061) + <code>^</code> (U+0302) y luego se recompone en <code>&#x60;â&#x60;</code> (U+00E2)</td>
    </tr>
    <tr>
      <td>NFKC (Normalization Form KC)</td>
      <td>Los caracteres se descomponen por compatibilidad y luego se recomponen por equivalencia canónica</td>
      <td><code>&#x60;ﬁ&#x60;</code> (U+FB01) se descompone en <code>f</code> (U+0066) + <code>i</code> (U+0069) y luego se recompone en <code>f</code> (U+0066) + <code>i</code> (U+0069)</td>
    </tr>
    <tr>
      <td>Lowercase</td>
      <td>Convierte el texto a minúsculas</td>
      <td><code>&#x60;Hello World&#x60;</code> se convierte en <code>hello world</code></td>
    </tr>
    <tr>
      <td>Strip</td>
      <td>Elimina todos los espacios en blanco de los lados especificados (izquierdo, derecho o ambos) del texto</td>
      <td><code>&#x60;  Hello World  &#x60;</code> se convierte en <code>Hello World</code></td>
    </tr>
    <tr>
      <td>StripAccents</td>
      <td>Elimina todos los símbolos de acento en unicode (se utilizará con NFD por coherencia)</td>
      <td><code>&#x60;á&#x60;</code> (U+00E1) se convierte en <code>a</code> (U+0061)</td>
    </tr>
    <tr>
      <td>Replace</td>
      <td>Sustituye una cadena personalizada o [regex](https://maximofn.com/regular-expressions/) y la cambia por el contenido dado</td>
      <td><code>&#x60;Hello World&#x60;</code> se convierte en <code>Hello Universe</code></td>
    </tr>
    <tr>
      <td>BertNormalizer</td>
      <td>Proporciona una implementación del Normalizador utilizado en el BERT original. Las opciones que se pueden configurar son <code>clean_text</code>, <code>handle_chinese_chars</code>, <code>strip_accents</code> y <code>lowercase</code></td>
      <td><code>&#x60;Hello World&#x60;</code> se convierte en <code>hello world</code></td>
    </tr>
  </tbody>
</table>'''
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_table_to_html_with_braces(self):
        markdown = '| Variable | Descripción |\n| --- | --- |\n| {{ .System }} | El mensaje del sistema utilizado para especificar un comportamiento personalizado. |\n| {{ .Prompt }} | El mensaje de aviso del usuario. |\n| {{ .Response }} | La respuesta del modelo. Al generar una respuesta, se omite el texto después de esta variable. |\n'
        expected_html = '''<table>
  <thead>
    <tr>
      <th>Variable</th>
      <th>Descripción</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>&#123;&#123; .System &#125;&#125;</td>
      <td>El mensaje del sistema utilizado para especificar un comportamiento personalizado.</td>
    </tr>
    <tr>
      <td>&#123;&#123; .Prompt &#125;&#125;</td>
      <td>El mensaje de aviso del usuario.</td>
    </tr>
    <tr>
      <td>&#123;&#123; .Response &#125;&#125;</td>
      <td>La respuesta del modelo. Al generar una respuesta, se omite el texto después de esta variable.</td>
    </tr>
  </tbody>
</table>'''
        self.assertEqual(markdown_table_to_html(markdown).strip(), expected_html.strip())

class TestMarkdownToHtml(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_markdown_to_html_with_text(self):
        markdown = """
# Hello World

This is a test of the markdown to html converter.
"""
        expected_html = """
<section class="section-block-markdown-cell">
<h1 id="Hello World">Hello World<a class="anchor-link" href="#Hello World">¶</a></h1>
<p>This is a test of the markdown to html converter.</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_with_inline_latex(self):
        markdown = 'La distancia euclídea entre dos puntos $p$ y $q$ se calcula como:'
        expected_html = """
<section class="section-block-markdown-cell">
<p>La distancia euclídea entre dos puntos <span class="math-inline">p</span> y <span class="math-inline">q</span> se calcula como:</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_latex_block(self):
        markdown = '$$\nd(p,q) = \\sqrt{(p_1 - q_1)^2 + (p_2 - q_2)^2 + \\cdots + (p_n - q_n)^2} = \\sqrt{\\sum_{i=1}^n (p_i - q_i)^2}\n$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">d(p,q) = &radic;((p<sub>1</sub> - q<sub>1</sub>)<sup>2</sup> + (p<sub>2</sub> - q<sub>2</sub>)<sup>2</sup> + ··· + (p<sub>n</sub> - q<sub>n</sub>)<sup>2</sup>) = &radic;(&sum;<sub>i=1</sub><sup>n</sup> (p<sub>i</sub> - q<sub>i</sub>)<sup>2</sup>)</span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_block_with_fractions(self):
        markdown = '$$\nsimilitud(U,V) = \\frac{U \\cdot V}{\\|U\\| \\|V\\|}\n$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">similitud(U,V) = <span class="math-fraction"><span class="math-fraction-numerator">U · V</span><span class="math-fraction-denominator">\\|U\\| \\|V\\|</span></span></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_latex_superscripts(self):
        markdown = '$$E = mc^2, x^{235}, a^{n+1}, e^{-x^2}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">E = mc<sup>2</sup>, x<sup>235</sup>, a<sup>n+1</sup>, e<sup>-x<sup>2</sup></sup></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_subscripts(self):
        markdown = '$$x_1, a_{123}, b_{n+1}, c_{i,j}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">x<sub>1</sub>, a<sub>123</sub>, b<sub>n+1</sub>, c<sub>i,j</sub></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_with_code(self):
        markdown = """
```python
print("Hello, World!")
```
"""
        expected_html = """
<section class="section-block-markdown-cell">
<div class='highlight'><pre><code class="language-python">print("Hello, World!")
</code></pre></div>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_with_code_and_text(self):
        markdown = """
# Hello World

This is a test of the markdown to html converter.

```python
print("Hello, World!")
```
"""
        expected_html = """
<section class="section-block-markdown-cell">
<h1 id="Hello World">Hello World<a class="anchor-link" href="#Hello World">¶</a></h1>
<p>This is a test of the markdown to html converter.</p>
<div class='highlight'><pre><code class="language-python">print("Hello, World!")
</code></pre></div>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_with_code_and_text_and_table(self):
        markdown = """
# Hello World

This is a test of the markdown to html converter.

```python
print("Hello, World!")
```

| Header 1 | Header 2 |
| -------- | -------- |
| Data 1   | Data 2   |
"""
        expected_html = """
<section class="section-block-markdown-cell">
<h1 id="Hello World">Hello World<a class="anchor-link" href="#Hello World">¶</a></h1>
<p>This is a test of the markdown to html converter.</p>
<div class='highlight'><pre><code class="language-python">print("Hello, World!")
</code></pre></div>
<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
    </tr>
  </tbody>
</table>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_with_code_and_text_and_table_and_image(self):
        markdown = """
# Hello World

This is a test of the markdown to html converter.

```python
print("Hello, World!")
```

| Header 1 | Header 2 |
| -------- | -------- |
| Data 1   | Data 2   |

![Image](https://example.com/image.png)
"""
        expected_html = """
<section class="section-block-markdown-cell">
<h1 id="Hello World">Hello World<a class="anchor-link" href="#Hello World">¶</a></h1>
<p>This is a test of the markdown to html converter.</p>
<div class='highlight'><pre><code class="language-python">print("Hello, World!")
</code></pre></div>
<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
    </tr>
  </tbody>
</table>
<img src="https://example.com/image.png" alt="Image">
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_with_code_and_text_and_table_and_image_and_link(self):

        markdown = """
# Hello World

This is a test of the markdown to html converter.

```python
print("Hello, World!")
```

| Header 1 | Header 2 |
| -------- | -------- |
| Data 1   | Data 2   |

![Image](https://example.com/image.png)

[Link](https://example.com)
"""
        expected_html = """
<section class="section-block-markdown-cell">
<h1 id="Hello World">Hello World<a class="anchor-link" href="#Hello World">¶</a></h1>
<p>This is a test of the markdown to html converter.</p>
<div class='highlight'><pre><code class="language-python">print("Hello, World!")
</code></pre></div>
<table>
  <thead>
    <tr>
      <th>Header 1</th>
      <th>Header 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Data 1</td>
      <td>Data 2</td>
    </tr>
  </tbody>
</table>
<img src="https://example.com/image.png" alt="Image">
<p><a href="https://example.com">Link</a></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_with_text_and_link(self):
        markdown = """`Whisper` es un sistema de reconocimiento automático de voz (automatic speech recognition (ASR)) entrenado en 680.000 horas de datos supervisados ​​multilingües y multitarea recopilados de la web. El uso de un conjunto de datos tan grande y diverso conduce a una mayor solidez ante los acentos, el ruido de fondo y el lenguaje técnico. Además, permite la transcripción en varios idiomas, así como la traducción de esos idiomas al inglés

[Website](https://openai.com/research/whisper)

[Paper](https://cdn.openai.com/papers/whisper.pdf)

[GitHub](https://github.com/openai/whisper)

[Model card](https://github.com/openai/whisper/blob/main/model-card.md)"""
        expected_html = '''<section class="section-block-markdown-cell">
<p><code>Whisper</code> es un sistema de reconocimiento automático de voz (automatic speech recognition (ASR)) entrenado en 680.000 horas de datos supervisados ​​multilingües y multitarea recopilados de la web. El uso de un conjunto de datos tan grande y diverso conduce a una mayor solidez ante los acentos, el ruido de fondo y el lenguaje técnico. Además, permite la transcripción en varios idiomas, así como la traducción de esos idiomas al inglés</p>
<p><a href="https://openai.com/research/whisper">Website</a></p>
<p><a href="https://cdn.openai.com/papers/whisper.pdf">Paper</a></p>
<p><a href="https://github.com/openai/whisper">GitHub</a></p>
<p><a href="https://github.com/openai/whisper/blob/main/model-card.md">Model card</a></p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_h1_whisper(self):
        markdown = "# Whisper"
        expected_html = '''<section class="section-block-markdown-cell">
<h1 id="Whisper">Whisper<a class="anchor-link" href="#Whisper">¶</a></h1>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_h2_introduccion(self):
        markdown = "## Introducción"
        expected_html = '''<section class="section-block-markdown-cell">
<h2 id="Introduccion">Introducción<a class="anchor-link" href="#Introduccion">¶</a></h2>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def text_with_code_inline(self):
        markdown = "`Whisper` es un sistema de reconocimiento automático de voz (automatic speech recognition (ASR)) entrenado en 680.000 horas de datos supervisados ​​multilingües y multitarea recopilados de la web. El uso de un conjunto de datos tan grande y diverso conduce a una mayor solidez ante los acentos, el ruido de fondo y el lenguaje técnico. Además, permite la transcripción en varios idiomas, así como la traducción de esos idiomas al inglés"
        expected_html = '''<section class="section-block-markdown-cell">
<p><code>Whisper</code> es un sistema de reconocimiento automático de voz (automatic speech recognition (ASR)) entrenado en 680.000 horas de datos supervisados ​​multilingües y multitarea recopilados de la web. El uso de un conjunto de datos tan grande y diverso conduce a una mayor solidez ante los acentos, el ruido de fondo y el lenguaje técnico. Además, permite la transcripción en varios idiomas, así como la traducción de esos idiomas al inglés</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_with_code_inline_with_two_apostrophes(self):
        markdown = 'El siguiente nivel es usar un LLM para responder al usuario. `FastRTC` viene con capacidades de ``speech-to-text`` y ``text-to-speech`` incorporadas, por lo que trabajar con LLMs es realmente fácil. Vamos a cambiar nuestra función `echo` en consecuencia:'
        expected_html = '''<section class="section-block-markdown-cell">
<p>El siguiente nivel es usar un LLM para responder al usuario. <code>FastRTC</code> viene con capacidades de <code>speech-to-text</code> y <code>text-to-speech</code> incorporadas, por lo que trabajar con LLMs es realmente fácil. Vamos a cambiar nuestra función <code>echo</code> en consecuencia:</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_link_to_external_url(self):
        markdown = "[Website](https://openai.com/research/whisper)"
        expected_html = '''<section class="section-block-markdown-cell">
<p><a href="https://openai.com/research/whisper">Website</a></p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_iframe_raw(self):
        markdown = """Cargamos el audio de este anuncio antiguo (de 1987) de Micro Machines

<iframe width="560" height="315" src="https://www.youtube.com/embed/zLP6oT3uqV8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>"""
        expected_html = '''<section class="section-block-markdown-cell">
<p>Cargamos el audio de este anuncio antiguo (de 1987) de Micro Machines</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/zLP6oT3uqV8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_iframe_converted(self):
        markdown = '''Cargamos el audio de este anuncio antiguo (de 1987) de Micro Machines

&lt;iframe width="560" height="315" src="https://www.youtube.com/embed/zLP6oT3uqV8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen&gt;&lt;/iframe&gt;'''
        expected_html = '''<section class="section-block-markdown-cell">
<p>Cargamos el audio de este anuncio antiguo (de 1987) de Micro Machines</p>
<iframe width="560" height="315" src="https://www.youtube.com/embed/zLP6oT3uqV8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_mixed_inline_and_display(self):
        markdown = 'La ecuación $E = mc^2$ es famosa. También tenemos: $$F = ma$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p>La ecuación <span class="math-inline">E = mc<sup>2</sup></span> es famosa. También tenemos: <span class="math-display">F = ma</span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_fractions(self):
        markdown = '$$\\frac{a}{b} = \\frac{c}{d}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display"><span class="math-fraction"><span class="math-fraction-numerator">a</span><span class="math-fraction-denominator">b</span></span> = <span class="math-fraction"><span class="math-fraction-numerator">c</span><span class="math-fraction-denominator">d</span></span></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_nested_fractions(self):
        markdown = '$$\\frac{\\frac{a}{b}}{\\frac{c}{d}} = \\frac{ad}{bc}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display"><span class="math-fraction"><span class="math-fraction-numerator"><span class="math-fraction"><span class="math-fraction-numerator">a</span><span class="math-fraction-denominator">b</span></span></span><span class="math-fraction-denominator"><span class="math-fraction"><span class="math-fraction-numerator">c</span><span class="math-fraction-denominator">d</span></span></span></span> = <span class="math-fraction"><span class="math-fraction-numerator">ad</span><span class="math-fraction-denominator">bc</span></span></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_fraction_with_superscripts(self):
        markdown = '$$\\frac{x^2 + 1}{x^3 - 1}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display"><span class="math-fraction"><span class="math-fraction-numerator">x<sup>2</sup> + 1</span><span class="math-fraction-denominator">x<sup>3</sup> - 1</span></span></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_inline_fraction(self):
        markdown = 'La derivada de $\\frac{x^2}{2}$ es $x$.'
        expected_html = """
<section class="section-block-markdown-cell">
<p>La derivada de <span class="math-inline"><span class="math-fraction"><span class="math-fraction-numerator">x<sup>2</sup></span><span class="math-fraction-denominator">2</span></span></span> es <span class="math-inline">x</span>.</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_complex_expression(self):
        markdown = '$$\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">&int;<sub>-&infin;</sub><sup>&infin;</sup> e<sup>-x<sup>2</sup></sup> dx = &radic;(&pi;)</span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_matrix_notation(self):
        markdown = '$$\\begin{matrix} a & b \\\\ c & d \\end{matrix}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">\\begin&#123;matrix&#125; a & b \\\\ c & d \\end&#123;matrix&#125;</span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_inline_with_subscripts_superscripts(self):
        markdown = 'La variable $x_i^2$ representa el cuadrado del elemento $i$-ésimo.'
        expected_html = """
<section class="section-block-markdown-cell">
<p>La variable <span class="math-inline">x<sub>i</sub><sup>2</sup></span> representa el cuadrado del elemento <span class="math-inline">i</span>-ésimo.</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_multiple_display_equations(self):
        markdown = '''Primera ecuación:
$$a^2 + b^2 = c^2$$

Segunda ecuación:
$$E = mc^2$$'''
        expected_html = """
<section class="section-block-markdown-cell">
<p>Primera ecuación:</p>
<p><span class="math-display">a<sup>2</sup> + b<sup>2</sup> = c<sup>2</sup></span></p>
<p>Segunda ecuación:</p>
<p><span class="math-display">E = mc<sup>2</sup></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_greek_letters(self):
        markdown = '$$\\alpha + \\beta = \\gamma, \\Delta = \\pi r^2$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">&alpha; + &beta; = &gamma;, \\Delta = &pi; r<sup>2</sup></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_summation_notation(self):
        markdown = '$$\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">&sum;<sub>i=1</sub><sup>n</sup> i = <span class="math-fraction"><span class="math-fraction-numerator">n(n+1)</span><span class="math-fraction-denominator">2</span></span></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_inline_in_paragraph(self):
        markdown = 'En física, la ecuación $E = mc^2$ relaciona la energía con la masa. También sabemos que $F = ma$ es la segunda ley de Newton.'
        expected_html = """
<section class="section-block-markdown-cell">
<p>En física, la ecuación <span class="math-inline">E = mc<sup>2</sup></span> relaciona la energía con la masa. También sabemos que <span class="math-inline">F = ma</span> es la segunda ley de Newton.</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_nested_superscripts(self):
        markdown = '$$e^{-x^{2}}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">e<sup>-x<sup>2</sup></sup></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_complex_subscripts(self):
        markdown = '$$x_{i,j}^{(k)} = a_{i+j}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">x<sub>i,j</sub><sup>(k)</sup> = a<sub>i+j</sub></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_integral_with_limits(self):
        markdown = '$$\\int_0^1 x^2 dx = \\frac{1}{3}$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">&int;<sub>0</sub><sup>1</sup> x<sup>2</sup> dx = <span class="math-fraction"><span class="math-fraction-numerator">1</span><span class="math-fraction-denominator">3</span></span></span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_mathematical_operators(self):
        markdown = '$$\\pm \\mp \\times \\div \\cdot \\ast$$'
        expected_html = """
<section class="section-block-markdown-cell">
<p><span class="math-display">&plusmn; \\mp &times; &divide; · \\ast</span></p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_empty_inline(self):
        markdown = 'Texto con matemáticas vacías $$ y más texto.'
        expected_html = """
<section class="section-block-markdown-cell">
<p>Texto con matemáticas vacías $$ y más texto.</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_latex_inline_with_text_around(self):
        markdown = 'Antes $x = 5$ después'
        expected_html = """
<section class="section-block-markdown-cell">
<p>Antes <span class="math-inline">x = 5</span> después</p>
</section>
"""
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_less_than_greater_than(self):
        markdown = 'Ahora que ya tenemos un entorno podemos ejecutar un script de dos maneras, la primera con `uv run python <script>.py`, que activará el entorno de `.venv` y ejecutará el script.'
        expected_html = '''<section class="section-block-markdown-cell">
<p>Ahora que ya tenemos un entorno podemos ejecutar un script de dos maneras, la primera con <code>uv run python &#x3C;script&#x3E;.py</code>, que activará el entorno de <code>.venv</code> y ejecutará el script.</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
      
    def test_markdown_to_html_link_with_slash_n(self):
        markdown = 'Como he dicho, estoy usando [LLMs-from-scratch/setup/01_optional-python-setup-preferences\n/native-uv.md](https://github.com/rasbt/LLMs-from-scratch/blob/main/setup/01_optional-python-setup-preferences/native-uv.md) como fuente, así que vamos a descargarnos el repositorio, instalar el entorno que propone y ver cómo ejecutar un script'
        expected_html = '''<section class="section-block-markdown-cell">
<p>Como he dicho, estoy usando <a href="https://github.com/rasbt/LLMs-from-scratch/blob/main/setup/01_optional-python-setup-preferences/native-uv.md">LLMs-from-scratch/setup/01_optional-python-setup-preferences/native-uv.md</a> como fuente, así que vamos a descargarnos el repositorio, instalar el entorno que propone y ver cómo ejecutar un script</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_title_with_inline_code(self):
        markdown = '## Instalar `uv`'
        expected_html = '''<section class="section-block-markdown-cell">
<h2 id="Instalar uv">Instalar <code>uv</code><a class="anchor-link" href="#Instalar uv">¶</a></h2>
</section>'''
        print("*"*100)
        print(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip())
        print(expected_html.strip())
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_link_and_text(self):
        markdown = '[Improving Language Understanding by Generative Pre-Training](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf) es el paper de GPT1. Antes de leer el post es necesario que te pongas en situación, antes de GPT los modelos de lenguaje estaban basados en redes recurrentes (RNN), que eran redes que funcionaban relativamente bien para tareas específicas, pero con las que no se podía reutilizar el preentrenamiento para hacerles un fine tuning para otras tareas. Además no tenían mucha memoria, por lo que si se le metían frases muy largas no recordaban muy bien el inicio de la frase'
        expected_html = '''<section class="section-block-markdown-cell">
<p><a href="https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf">Improving Language Understanding by Generative Pre-Training</a> es el paper de GPT1. Antes de leer el post es necesario que te pongas en situación, antes de GPT los modelos de lenguaje estaban basados en redes recurrentes (RNN), que eran redes que funcionaban relativamente bien para tareas específicas, pero con las que no se podía reutilizar el preentrenamiento para hacerles un fine tuning para otras tareas. Además no tenían mucha memoria, por lo que si se le metían frases muy largas no recordaban muy bien el inicio de la frase</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_blockcuote(self):
        markdown = '> Reiniciamos el notebook para que no haya problemas con la memoria de la GPU'
        expected_html = '''<section class="section-block-markdown-cell">
<blockquote>
<p>Reiniciamos el notebook para que no haya problemas con la memoria de la GPU</p>
</blockquote>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
      
    def test_markdown_to_html_iframe_with_text(self):
        markdown = '<iframe>\n\tsrc="https://xenova-the-tokenizer-playground.static.hf.space"\n\tframeborder="0"\n\twidth="850"\n\theight="450"\n></iframe>'
        expected_html = '''<section class="section-block-markdown-cell">
<iframe src="https://xenova-the-tokenizer-playground.static.hf.space" frameborder="0" width="850" height="450"></iframe>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_open_trace(self):
        markdown = 'Supongamos que para una entrada $x$ queremos que tenga una salida $\\hat{y}$'
        expected_html = '''<section class="section-block-markdown-cell">
<p>Supongamos que para una entrada <span class="math-inline">x</span> queremos que tenga una salida <span class="math-inline">\\hat&#123;y&#125;</span></p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_open_trace_2(self):
        markdown = '```md\n``json\n{\n  "query": "Your question here",\n  "thread_id": "optional_thread_identifier"\n}\n``\n```'
        expected_html = '''<section class="section-block-markdown-cell">
<pre><code class="language-md">
```json
&#123;
  "query": "Your question here",
  "thread_id": "optional_thread_identifier"
&#125;
```
</code></pre>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())
    
    def test_markdown_to_html_code_open_backslash(self):
        markdown = "\n                  __    __    __    __\n                 /  \\  /  \\  /  \\  /  \\\n                /    \\/    \\/    \\/    \\\n███████████████/  /██/  /██/  /██/  /████████████████████████"
        expected_html = '''<section class="section-block-markdown-cell">
<p>__    __    __    __</p>
<p>/  \  /  \  /  \  /  \</p>
<p>/    \/    \/    \/    \</p>
<p>███████████████/  /██/  /██/  /██/  /████████████████████████</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

    def test_markdown_to_html_code_title_with_braces_into_code(self):
        markdown = "Le pedimos los issues del repositorio `transformers` de `huggingface`. Tras pensar un rato nos dice que va a usar la `tool` `list_repository_issues` con los argumentos `{'owner': 'huggingface', 'repo_name': 'transformers'}`."
        expected_html = '''<section class="section-block-markdown-cell">
<p>Le pedimos los issues del repositorio <code>transformers</code> de <code>huggingface</code>. Tras pensar un rato nos dice que va a usar la <code>tool</code> <code>list_repository_issues</code> con los argumentos <code>&#123;'owner': 'huggingface', 'repo_name': 'transformers'&#125;</code>.</p>
</section>'''
        self.assertEqual(jupyter_notebook_contents_in_xml_format_to_html(markdown).strip(), expected_html.strip())

if __name__ == '__main__':
    # It's good practice to ensure that only one unittest.main() call remains,
    # especially if tests might interfere (though less likely with simple unit tests).
    # For this combined file, one main call is sufficient.
    unittest.main()
