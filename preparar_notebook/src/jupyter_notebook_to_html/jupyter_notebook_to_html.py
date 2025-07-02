import re
import unicodedata
from .generic_markdown_to_specific_markdowns import generic_markdown_to_list_specific_markdowns
from .markdown_code_to_html_converter import markdown_code_to_html as convert_code_to_html
from .markdown_image_to_html import markdown_image_to_html as convert_image_to_html
from .markdown_link_to_html import markdown_to_html_external_link, markdown_to_html_internal_link
from .markdown_lists_to_html import markdown_to_html_updated as convert_list_to_html
from .markdown_table_to_html import markdown_table_to_html as convert_table_to_html

def _remove_accents(text: str) -> str:
    """
    Removes accents from text using Unicode normalization.
    """
    # Normalize to NFD (decomposed form) and filter out accent marks
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')

def _process_inline_code(text: str) -> str:
    """
    Processes inline code (text between single backticks) in a text string.
    Converts `code` to <code>code</code>.
    """
    # Pattern to match inline code: `text`
    # Use non-greedy matching to handle multiple inline code blocks in one line
    pattern = r'`([^`]+)`'
    
    def replace_inline_code(match):
        code_content = match.group(1)
        return f'<code>{code_content}</code>'
    
    return re.sub(pattern, replace_inline_code, text)

def _process_inline_links(text: str) -> str:
    """
    Processes inline links in a text string.
    Converts [text](url) to appropriate HTML link tags.
    """
    # First process external links (http:// or https://)
    external_pattern = r'\[([^\]]*)\]\((https?://[^\)]+)\)'
    def replace_external_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        return f'<a href="{link_url}">{link_text}</a>'
    text = re.sub(external_pattern, replace_external_link, text)
    
    # Then process internal links (starting with /)
    internal_pattern = r'\[([^\]]*)\]\((/[^\)]*)\)'
    def replace_internal_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        return f'<a href="{link_url}">{link_text}</a>'
    text = re.sub(internal_pattern, replace_internal_link, text)
    
    return text

def _process_text_block(text_content: str) -> str:
    """
    Processes a 'text' block, converting Markdown headers and paragraphs to HTML.
    """
    def create_header_with_anchor(level: int, title: str) -> str:
        """Creates an HTML header with ID and anchor link."""
        # Use the original title for display (with accents)
        corrected_title = title.strip()
        
        # Create ID without accents (normalize for URL-friendly IDs)
        header_id = _remove_accents(title.strip())
        
        # Create the header with anchor link
        return f'<h{level} id="{header_id}">{corrected_title}<a class="anchor-link" href="#{header_id}">¶</a></h{level}>'
    
    # Handle headers (H1 to H6) with anchor links
    # Order matters: H6 before H1 to avoid partial matches
    text_content = re.sub(r"^\s*###### (.*)", lambda m: create_header_with_anchor(6, m.group(1)), text_content, flags=re.MULTILINE)
    text_content = re.sub(r"^\s*##### (.*)", lambda m: create_header_with_anchor(5, m.group(1)), text_content, flags=re.MULTILINE)
    text_content = re.sub(r"^\s*#### (.*)", lambda m: create_header_with_anchor(4, m.group(1)), text_content, flags=re.MULTILINE)
    text_content = re.sub(r"^\s*### (.*)", lambda m: create_header_with_anchor(3, m.group(1)), text_content, flags=re.MULTILINE)
    text_content = re.sub(r"^\s*## (.*)", lambda m: create_header_with_anchor(2, m.group(1)), text_content, flags=re.MULTILINE)
    text_content = re.sub(r"^\s*# (.*)", lambda m: create_header_with_anchor(1, m.group(1)), text_content, flags=re.MULTILINE)

    # Wrap remaining lines that are not headers in <p> tags
    # This is a simplified approach. True paragraph handling is more complex.
    processed_lines = []
    for line in text_content.split('\n'):
        if line.strip() == "":
            continue # Skip empty lines for now, though they might signify paragraph breaks
        if re.match(r"<h[1-6].*</h[1-6]>", line.strip()):
            processed_lines.append(line.strip())
        else:
            # Avoid wrapping already wrapped content or things that shouldn't be wrapped
            # This is a basic check.
            if not line.strip().startswith("<"): # Simplistic check
                # Process inline code and links before wrapping in <p> tags
                processed_line = _process_inline_code(line.strip())
                processed_line = _process_inline_links(processed_line)
                processed_lines.append(f"<p>{processed_line}</p>")
            else: # Already some HTML, or other structure
                 processed_lines.append(line.strip())

    return "\n".join(processed_lines)


def jupyter_notebook_contents_in_xml_format_to_html(list_of_jupyter_notebook_contents_in_xml_format):
    """
    Converts a list of content blocks or a single markdown string to HTML.
    Each content block is a dictionary with a type (e.g., "markdown", "input_code")
    and its content.
    """
    html_output_parts = []

    # If the input is a single string, treat it as a single "markdown" block.
    # This is to align with the test cases like `test_markdown_to_html_with_text`
    # which pass a raw markdown string directly.
    if isinstance(list_of_jupyter_notebook_contents_in_xml_format, str):
        list_of_contents = [{"markdown": list_of_jupyter_notebook_contents_in_xml_format}]
    elif isinstance(list_of_jupyter_notebook_contents_in_xml_format, list):
        list_of_contents = list_of_jupyter_notebook_contents_in_xml_format
    else:
        raise TypeError("Input must be a markdown string or a list of content blocks.")

    for item in list_of_contents:
        if "markdown" in item:
            markdown_content = item["markdown"]
            # Break down the generic markdown into specific parts
            specific_markdowns = generic_markdown_to_list_specific_markdowns(markdown_content)

            # Wrap the specific markdown blocks in a section
            html_output_parts.append(f'<section class="section-block-markdown-cell">')

            for specific_block in specific_markdowns:
                block_type, block_content = list(specific_block.items())[0]

                if block_type == "text":
                    # Text blocks might contain headers or simple paragraphs.
                    # The generic_markdown_to_specific_markdowns might return larger text blocks
                    # that need further processing for headers, paragraphs etc.
                    html_output_parts.append(_process_text_block(block_content))
                elif block_type == "code":
                    html_output_parts.append(convert_code_to_html(block_content, include_language_class=True))
                elif block_type == "table":
                    html_output_parts.append(convert_table_to_html(block_content))
                elif block_type == "list":
                    html_output_parts.append(convert_list_to_html(block_content))
                elif block_type == "link":
                    # Need to determine if it's internal or external
                    # The generic_markdown_to_specific_markdowns should ideally give us this info,
                    # or the link converters need to be smart enough.
                    # Current generic_markdown_to_specific_markdowns transforms known internal links.
                    # We can check the pattern.
                    if re.match(r"\[.*\]\((https?://.*)\)", block_content):
                        link_html = markdown_to_html_external_link(block_content)
                        html_output_parts.append(f"<p>{link_html}</p>")
                    elif re.match(r"\[.*\]\((/.*)\)", block_content): # Matches /path type links
                        link_html = markdown_to_html_internal_link(block_content)
                        html_output_parts.append(f"<p>{link_html}</p>")
                    else:
                        # Fallback or unhandled link type, pass as is or wrap in <p>?
                        # For now, pass as is, which _process_text_block might wrap in <p> if it was part of text
                        html_output_parts.append(_process_text_block(block_content))
                elif block_type == "image":
                    # Images are often inline, _process_text_block might be more appropriate
                    # if they are not on their own line. However, generic_markdown_to_specific_markdowns
                    # seems to separate them if they are distinct.
                    # The test `test_markdown_to_html_with_code_and_text_and_table_and_image` implies
                    # an image is converted directly.
                    html_output_parts.append(convert_image_to_html(block_content))
                else:
                    # Unknown specific markdown type, treat as text for now
                    html_output_parts.append(_process_text_block(block_content))
            
            # Close the section
            html_output_parts.append(f"</section>")

        elif "input_code" in item:
            code_content = item["input_code"]
            # Assuming input_code should also be wrapped like markdown code blocks
            # The markdown_code_to_html_converter.py expects ```python ... ``` format.
            # We might need a simpler wrapper or adapt. For now, let's assume raw code.
            # The tests don't explicitly cover 'input_code' or 'output_code' blocks directly
            # in TestMarkdownToHtml, but good practice to handle them.
            # Let's wrap in simple pre/code tags.
            escaped_code = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_output_parts.append(f"<pre><code>{escaped_code}</code></pre>")
        
        elif "output_code" in item:
            code_content = item["output_code"]
            escaped_code = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_output_parts.append(f"<pre><code>{escaped_code}</code></pre>")
        
        # else:
            # Potentially other types of content blocks if the structure evolves.

    # Join parts and wrap in section element as expected by tests
    html_content = "\n".join(filter(None, html_output_parts)).strip()
    
    # Wrap everything in a section element as expected by the tests
    if html_content:
        return html_content
    else:
        return ""

# Example usage (optional, for testing)
if __name__ == '__main__':
    sample_markdown_string = """
# Title

Some text.

```python
print("hello")
```

- list item 1
- list item 2

[External Link](https://example.com)

![Alt Text](image.png)
"""
    html_result = jupyter_notebook_contents_in_xml_format_to_html(sample_markdown_string)
    print(html_result)

    sample_content_list = [
        {"markdown": "# Hello World\nThis is a test."},
        {"input_code": "print('Input here')"},
        {"markdown": "Another markdown block with a table:\n| A | B |\n|---|---|\n| 1 | 2 |"},
        {"output_code": "Output from code"}
    ]
    html_result_list = jupyter_notebook_contents_in_xml_format_to_html(sample_content_list)
    print("\n--- From List ---\n")
    print(html_result_list)
