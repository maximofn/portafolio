import re
import html

def markdown_code_to_html(markdown_content: str) -> str:
    """
    Converts a Markdown code block to HTML.

    Args:
        markdown_content: The Markdown string.

    Returns:
        The HTML representation of the code block, or the original content if no code block is found.
    """
    # Pattern to capture the language (optional) and the code content
    # Handles optional language specifier, and potential leading/trailing whitespace around the block
    pattern = r"```(?:\s*(\w+))?\s*\n(.*?)\n```"

    match = re.search(pattern, markdown_content, re.DOTALL)

    if match:
        # language = match.group(1) # Language specifier, if present
        code_content = match.group(2)

        # Escape HTML characters, then specifically replace &#x27; with &#39; for test compatibility
        escaped_code = html.escape(code_content).replace('&#x27;', '&#39;')

        return f"<pre><code>{escaped_code}\n</code></pre>\n"
    else:
        return markdown_content
