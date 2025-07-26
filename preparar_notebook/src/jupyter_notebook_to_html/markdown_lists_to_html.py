import re

def convert_latex_symbols_to_html(text: str) -> str:
    r"""
    Converts LaTeX mathematical symbols to HTML entities.
    
    Args:
        text: LaTeX text containing mathematical symbols
        
    Returns:
        HTML text with LaTeX symbols converted to HTML entities
    """
    def replace_sqrt_with_balanced_braces(text: str) -> str:
        """
        Replaces \sqrt{...} with &radic;(...) handling nested braces correctly.
        """
        result = []
        i = 0
        while i < len(text):
            if text[i:].startswith(r'\sqrt{'):
                # Found \sqrt{, now find the matching closing brace
                start_pos = i + 6  # Position after '\sqrt{'
                brace_count = 1
                j = start_pos
                
                while j < len(text) and brace_count > 0:
                    if text[j] == '{':
                        brace_count += 1
                    elif text[j] == '}':
                        brace_count -= 1
                    j += 1
                
                if brace_count == 0:
                    # Found matching closing brace
                    content = text[start_pos:j-1]  # Content between braces
                    result.append(f'&radic;({content})')
                    i = j
                else:
                    # No matching closing brace found, keep original
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    def replace_superscripts_with_html(text: str) -> str:
        """
        Replaces ^{...} and ^n with <sup>...</sup> handling nested expressions correctly.
        """
        result = []
        i = 0
        while i < len(text):
            if i < len(text) - 1 and text[i] == '^':
                if i + 1 < len(text) and text[i + 1] == '{':
                    # Found ^{, now find the matching closing brace
                    start_pos = i + 2  # Position after '^{'
                    brace_count = 1
                    j = start_pos
                    
                    while j < len(text) and brace_count > 0:
                        if text[j] == '{':
                            brace_count += 1
                        elif text[j] == '}':
                            brace_count -= 1
                        j += 1
                    
                    if brace_count == 0:
                        # Found matching closing brace
                        content = text[start_pos:j-1]  # Content between braces
                        # Recursively process the content in case there are nested superscripts
                        processed_content = replace_superscripts_with_html(content)
                        result.append(f'<sup>{processed_content}</sup>')
                        i = j
                    else:
                        # No matching closing brace found, keep original
                        result.append(text[i])
                        i += 1
                elif i + 1 < len(text) and (text[i + 1].isalnum() or text[i + 1] in '-+'):
                    # Found ^n format (single character or number, including negative)
                    start_pos = i + 1
                    j = start_pos
                    
                    # Handle negative sign
                    if text[j] == '-' or text[j] == '+':
                        j += 1
                    
                    # Collect consecutive alphanumeric characters
                    while j < len(text) and text[j].isalnum():
                        j += 1
                    
                    if j > start_pos:
                        content = text[start_pos:j]
                        result.append(f'<sup>{content}</sup>')
                        i = j
                    else:
                        # No valid superscript content found
                        result.append(text[i])
                        i += 1
                else:
                    # ^ not followed by { or alphanumeric, keep original
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)

    def replace_subscripts_with_html(text: str) -> str:
        """
        Replaces _{...} and _n with <sub>...</sub> handling nested expressions correctly.
        """
        result = []
        i = 0
        while i < len(text):
            if i < len(text) - 1 and text[i] == '_':
                if i + 1 < len(text) and text[i + 1] == '{':
                    # Found _{, now find the matching closing brace
                    start_pos = i + 2  # Position after '_{'
                    brace_count = 1
                    j = start_pos
                    
                    while j < len(text) and brace_count > 0:
                        if text[j] == '{':
                            brace_count += 1
                        elif text[j] == '}':
                            brace_count -= 1
                        j += 1
                    
                    if brace_count == 0:
                        # Found matching closing brace
                        content = text[start_pos:j-1]  # Content between braces
                        # Recursively process the content in case there are nested subscripts
                        processed_content = replace_subscripts_with_html(content)
                        result.append(f'<sub>{processed_content}</sub>')
                        i = j
                    else:
                        # No matching closing brace found, keep original
                        result.append(text[i])
                        i += 1
                elif i + 1 < len(text) and (text[i + 1].isalnum() or text[i + 1] in '-+'):
                    # Found _n format (single character or number, including negative)
                    start_pos = i + 1
                    j = start_pos
                    
                    # Handle negative sign
                    if text[j] == '-' or text[j] == '+':
                        j += 1
                    
                    # Collect consecutive alphanumeric characters
                    while j < len(text) and text[j].isalnum():
                        j += 1
                    
                    if j > start_pos:
                        content = text[start_pos:j]
                        result.append(f'<sub>{content}</sub>')
                        i = j
                    else:
                        # No valid subscript content found
                        result.append(text[i])
                        i += 1
                else:
                    # _ not followed by { or alphanumeric, keep original
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)

    def replace_fractions_with_html(text: str) -> str:
        """
        Replaces \\frac{numerator}{denominator} with HTML fraction structure.
        """
        result = []
        i = 0
        while i < len(text):
            if text[i:].startswith(r'\frac{'):
                # Found \frac{, now find the numerator and denominator
                start_pos = i + 6  # Position after '\frac{'
                brace_count = 1
                j = start_pos
                
                # Find the end of the numerator
                while j < len(text) and brace_count > 0:
                    if text[j] == '{':
                        brace_count += 1
                    elif text[j] == '}':
                        brace_count -= 1
                    j += 1
                
                if brace_count == 0 and j < len(text) and text[j] == '{':
                    # Found numerator, now find denominator
                    numerator = text[start_pos:j-1]
                    
                    # Start finding denominator
                    denom_start = j + 1  # Position after second '{'
                    brace_count = 1
                    k = denom_start
                    
                    while k < len(text) and brace_count > 0:
                        if text[k] == '{':
                            brace_count += 1
                        elif text[k] == '}':
                            brace_count -= 1
                        k += 1
                    
                    if brace_count == 0:
                        # Found complete fraction
                        denominator = text[denom_start:k-1]
                        
                        # Recursively process numerator and denominator for nested expressions
                        processed_numerator = convert_latex_symbols_to_html(numerator)
                        processed_denominator = convert_latex_symbols_to_html(denominator)
                        
                        fraction_html = f'<span class="math-fraction"><span class="math-fraction-numerator">{processed_numerator}</span><span class="math-fraction-denominator">{processed_denominator}</span></span>'
                        result.append(fraction_html)
                        i = k
                    else:
                        # No matching closing brace for denominator
                        result.append(text[i])
                        i += 1
                else:
                    # No denominator found or malformed fraction
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        return ''.join(result)
    
    # First handle \sqrt{} with balanced braces
    text = replace_sqrt_with_balanced_braces(text)
    
    # Then handle superscripts ^{...} and ^n
    text = replace_superscripts_with_html(text)
    
    # Then handle subscripts _{...} and _n
    text = replace_subscripts_with_html(text)
    
    # Note: For lists, we don't convert fractions to HTML structure
    # Instead, we keep the LaTeX format and just escape the braces later
    
    # Dictionary mapping other LaTeX symbols to HTML entities
    latex_to_html = {
        r'\\cdots': r'···',                     # Centered dots: \cdots -> ···
        r'\\cdot': r'·',                        # Centered dot: \cdot -> ·
        r'\\sum': r'&sum;',                     # Summation: \sum -> ∑
        r'\\prod': r'&prod;',                   # Product: \prod -> ∏
        r'\\int': r'&int;',                     # Integral: \int -> ∫
        r'\\alpha': r'&alpha;',                 # Alpha: \alpha -> α
        r'\\beta': r'&beta;',                   # Beta: \beta -> β
        r'\\gamma': r'&gamma;',                 # Gamma: \gamma -> γ
        r'\\delta': r'&delta;',                 # Delta: \delta -> δ
        r'\\epsilon': r'&epsilon;',             # Epsilon: \epsilon -> ε
        r'\\theta': r'&theta;',                 # Theta: \theta -> θ
        r'\\lambda': r'&lambda;',               # Lambda: \lambda -> λ
        r'\\mu': r'&mu;',                       # Mu: \mu -> μ
        r'\\pi': r'&pi;',                       # Pi: \pi -> π
        r'\\sigma': r'&sigma;',                 # Sigma: \sigma -> σ
        r'\\tau': r'&tau;',                     # Tau: \tau -> τ
        r'\\phi': r'&phi;',                     # Phi: \phi -> φ
        r'\\omega': r'&omega;',                 # Omega: \omega -> ω
        r'\\infty': r'&infin;',                 # Infinity: \infty -> ∞
        r'\\pm': r'&plusmn;',                   # Plus-minus: \pm -> ±
        r'\\times': r'&times;',                 # Multiplication: \times -> ×
        r'\\div': r'&divide;',                  # Division: \div -> ÷
        r'\\le': r'&le;',                       # Less than or equal: \le -> ≤
        r'\\ge': r'&ge;',                       # Greater than or equal: \ge -> ≥
        r'\\ne': r'&ne;',                       # Not equal: \ne -> ≠
        r'\\approx': r'&asymp;',                # Approximately equal: \approx -> ≈
    }
    
    # Note: For lists, we don't convert LaTeX symbols to HTML entities
    # Instead, we keep the LaTeX format and just escape the braces
    # Apply all other replacements
    # for latex_pattern, html_replacement in latex_to_html.items():
    #     text = re.sub(latex_pattern, html_replacement, text)
    
    # Finally, escape any remaining curly braces that weren't part of processed LaTeX commands
    # This handles cases like \hat{y} where the braces should be escaped as HTML entities
    text = text.replace('{', '&#123;').replace('}', '&#125;')
    
    return text

def process_links_in_text(text):
    """
    Processes both internal and external markdown links, inline code, bold text, and inline math in a text string.
    
    Args:
        text: Text that may contain markdown links, inline code, bold text, and inline math
        
    Returns:
        Text with markdown links, inline code, bold text, and inline math converted to HTML
    """
    # Store processed code blocks to avoid processing their content again
    code_placeholders = {}
    placeholder_counter = 0
    
    # Helper function to escape HTML special characters in code content and store it
    def escape_braces_in_code(match):
        nonlocal placeholder_counter
        code_content = match.group(1)
        
        # Escape HTML tags but only if they are actual HTML elements
        def escape_html_tags(text):
            import re
            
            # List of common HTML tags that should be escaped
            html_tags = {
                'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 
                'blockquote', 'body', 'br', 'button', 'canvas', 'caption', 'cite', 'code', 'col', 
                'colgroup', 'data', 'datalist', 'dd', 'del', 'details', 'dfn', 'dialog', 'div', 'dl', 
                'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure', 'footer', 'form', 'h1', 'h2', 
                'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hgroup', 'hr', 'html', 'i', 'iframe', 
                'img', 'input', 'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main', 'map', 'mark', 
                'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup', 'option', 'output', 
                'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby', 's', 'samp', 
                'script', 'section', 'select', 'small', 'source', 'span', 'strong', 'style', 'sub', 
                'summary', 'sup', 'svg', 'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 
                'th', 'thead', 'time', 'title', 'tr', 'track', 'u', 'ul', 'var', 'video', 'wbr'
            }
            
            # Pattern to match tags: <tagname> or <tagname attributes> or </tagname>
            html_tag_pattern = r'<(/?)([a-zA-Z][a-zA-Z0-9]*)((?:\s+[^>]*)?)\s*>'
            
            def replace_tag(match):
                slash = match.group(1)  # '/' for closing tags
                tag_name = match.group(2).lower()  # tag name
                attributes = match.group(3) or ''  # attributes
                
                # Only escape if it's a known HTML tag
                if tag_name in html_tags:
                    return f'&lt;{slash}{tag_name}{attributes}&gt;'
                else:
                    # Not a known HTML tag, leave it as is
                    return match.group(0)
            
            return re.sub(html_tag_pattern, replace_tag, text)
        
        # Escape all braces in code content
        def escape_all_braces(text):
            # Simply escape all { and } to HTML entities
            text = text.replace('{', '&#123;').replace('}', '&#125;')
            return text
        
        # Apply HTML tag escaping
        code_content = escape_html_tags(code_content)
        
        # Apply brace escaping - escape all braces
        code_content = escape_all_braces(code_content)
        
        final_code = f'<code>{code_content}</code>'
        
        # Create a unique placeholder
        placeholder = f'__CODE_PLACEHOLDER_{placeholder_counter}__'
        code_placeholders[placeholder] = final_code
        placeholder_counter += 1
        
        return placeholder
    
    # IMPORTANT: Process inline code FIRST to prevent $ symbols inside code from being treated as math
    # First process inline code with double backticks
    text = re.sub(r'``([^`]+?)``', escape_braces_in_code, text)
    
    # Then process inline code with single backticks (but not those already processed)
    text = re.sub(r'`([^`]+?)`', escape_braces_in_code, text)
    
    # Process bold text (**text**) to <strong>text</strong>
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<strong>\1</strong>', text)
    
    # Process inline math (text between single dollar signs)
    def process_inline_math(match):
        math_content = match.group(1)
        # Convert LaTeX symbols to HTML entities including escaping braces
        math_content = convert_latex_symbols_to_html(math_content)
        return f'<span class="math-inline">{math_content}</span>'
    
    # Now process math - code placeholders won't be affected
    text = re.sub(r'\$([^$]+?)\$', process_inline_math, text)
    
    # Then process external links (https:// or http://)
    text = re.sub(r'\[(.*?)\]\((https?://.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Finally process internal links (starting with /)
    text = re.sub(r'\[(.*?)\]\((/.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Restore code placeholders with their final HTML
    for placeholder, code_html in code_placeholders.items():
        text = text.replace(placeholder, code_html)
    
    return text

def markdown_unordered_list_to_html(markdown_text):
    """
    Converts a Markdown unordered list to HTML.

    Args:
        markdown_text: A string containing Markdown unordered list.

    Returns:
        A string containing the HTML representation of the list.
    """
    if not markdown_text.strip():
        return ""

    lines = markdown_text.strip().split('\n')
    html_output = "<ul>\n"
    list_stack = [] # To handle nesting levels

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # Determine the indentation level
        indentation = len(line) - len(line.lstrip())
        level = indentation // 2  # Assuming 2 spaces for indentation, can be adjusted

        if not (stripped_line.startswith('- ') or stripped_line.startswith('* ') or stripped_line.startswith('+ ')):
            # If a line is not a list item, and we are in a list, close it.
            # This handles cases where non-list text might be mixed, though the primary goal is list conversion.
            if list_stack:
                while list_stack:
                    html_output += "</ul>\n"
                    list_stack.pop()
            # For simplicity, we'll assume the input is primarily a list.
            # Non-list items within a list structure are not strictly handled by this basic converter.
            # A more robust parser would be needed for complex documents.
            continue # Skip non-list item lines for now

        item_text = stripped_line[2:] # Remove the marker (e.g., '- ', '* ')

        if not list_stack: # First item
            list_stack.append(level)
        elif level > list_stack[-1]: # New nested list
            html_output += "<ul>\n"
            list_stack.append(level)
        elif level < list_stack[-1]: # Closing nested list(s)
            while list_stack and level < list_stack[-1]:
                html_output += "</ul>\n"
                list_stack.pop()
            if not list_stack or level != list_stack[-1]: # Should not happen in well-formed markdown
                # This case implies malformed markdown or mixed content not fully supported.
                # For now, we'll treat it as a new list at the current level if stack is empty
                # or adjust if needed. This part might need refinement for complex cases.
                if not list_stack:
                    html_output += "<ul>\n" # Start a new list if stack became empty
                    list_stack.append(level)


        html_output += f"  <li>{item_text}</li>\n"

    # Close any remaining open tags
    while list_stack:
        html_output += "</ul>\n"
        list_stack.pop()

    # Remove the initial <ul> if no items were added (e.g. empty input after stripping)
    # This check needs to be more robust. A better way is to build items and then wrap.
    # For now, if html_output is just "<ul>\n</ul>\n" (or similar for empty list), it's okay.
    # A quick check: if html_output is effectively empty of actual list items.
    if html_output == "<ul>\n" + "</ul>\n" * (html_output.count("</ul>") -1) and "<li>" not in html_output:
         return ""


    return html_output.strip()


def markdown_to_html_updated(markdown_text):
    """
    Converts Markdown text with unordered lists (including nested ones) to HTML.
    Handles lists starting with '-', '*', or '+'.
    Indentation (2 spaces) determines nesting.
    Also handles ordered lists.
    """
    lines = markdown_text.strip().split('\n')
    html_lines = []
    list_level_markers = {}  # Stores the type of list ('ul' or 'ol') at each level

    # Regex for ordered list items (e.g., "1. item", "01. item")
    ordered_item_pattern = re.compile(r"^\s*(\d+)\.\s+(.*)")

    def get_indent_level(line_text):
        leading_spaces = 0
        for char in line_text:
            if char == ' ':
                leading_spaces += 1
            else:
                break
        return leading_spaces // 2

    def close_lists(current_level, current_indent_level=None):
        closed_html = ""
        # Iterate over a copy of keys for safe deletion
        levels_to_close = sorted([lvl for lvl in list_level_markers if lvl > current_level], reverse=True)

        # If current_indent_level is provided, also close lists at the same level
        # if the list type is changing or if it's a non-list item forcing closure.
        if current_indent_level is not None and current_indent_level in list_level_markers:
            # This condition is tricky: only close if type is changing or forced by non-list.
            # For now, close_lists is mostly for deeper levels or complete closure.
            # The main loop will handle same-level type changes.
            pass # This specific scenario is better handled in the main loop.

        for lvl in levels_to_close:
            tag = 'ul' if list_level_markers[lvl] == 'ul' else 'ol'
            closed_html += "  " * lvl + f"</{tag}>\n"
            del list_level_markers[lvl]
        return closed_html

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            # Preserve blank lines if they are not within a list context,
            # or handle them according to Markdown rules (often ignored in lists).
            # For simplicity, we'll just continue, which means blank lines might interrupt lists
            # if not handled carefully by list start/end logic.
            # If we are inside a list, blank lines are typically ignored or end the list.
            # The current logic will likely break lists on blank lines if not careful.
            # A more robust parser might need to look ahead or track "within list" state.
            continue

        indent_level = get_indent_level(line)

        # Try to match ordered list first
        ordered_match = ordered_item_pattern.match(stripped_line)
        is_unordered_list_item = stripped_line.startswith(('-', '*', '+')) and stripped_line[1:2] == ' '

        current_list_type = None
        item_content = ""

        if ordered_match:
            current_list_type = 'ol'
            # item_content = ordered_match.group(1) # This was the number, we need the text
            item_content = process_links_in_text(ordered_match.group(2).strip())
        elif is_unordered_list_item:
            current_list_type = 'ul'
            item_content = process_links_in_text(line.strip()[2:].strip())

        if current_list_type:
            # Close lists that are deeper than the current item's level
            html_lines.append(close_lists(indent_level))

            # Handle change in list type at the same level or start of a new list
            if indent_level not in list_level_markers or list_level_markers[indent_level] != current_list_type:
                # If a list of a different type exists at this level, close it first
                if indent_level in list_level_markers and list_level_markers[indent_level] != current_list_type:
                    old_tag = 'ul' if list_level_markers[indent_level] == 'ul' else 'ol'
                    html_lines.append("  " * indent_level + f"</{old_tag}>\n")

                # Start the new list
                list_level_markers[indent_level] = current_list_type
                tag = 'ul' if current_list_type == 'ul' else 'ol'
                html_lines.append("  " * indent_level + f"<{tag}>\n")

            # Add the list item
            html_lines.append("  " * (indent_level + 1) + f"<li>{item_content}</li>\n")
        else:
            # Non-list item, close all open lists
            html_lines.append(close_lists(-1)) # -1 ensures all levels are considered "deeper"
            html_lines.append(f"<p>{stripped_line}</p>\n")

    # Close any remaining open lists at the end
    html_lines.append(close_lists(-1))

    return "".join(html_lines).strip()


def markdown_ordered_list_to_html(markdown_text):
    """
    Converts a Markdown ordered list to HTML.

    Args:
        markdown_text: A string containing Markdown ordered list.

    Returns:
        A string containing the HTML representation of the list.
    """
    if not markdown_text.strip():
        return ""

    lines = markdown_text.strip().split('\n')
    html_output = "<ol>\n"
    list_stack = []  # To handle nesting levels (indentation)
    # Regex to capture item number and text for ordered lists
    # Allows for optional spaces around the number and dot
    ordered_item_pattern = re.compile(r"^\s*(\d+)\.\s+(.*)")

    for line in lines:
        original_line = line # Keep original line for indentation calculation
        stripped_line = line.strip()

        if not stripped_line:
            continue

        match = ordered_item_pattern.match(stripped_line)
        if not match:
            # If a line is not a list item, and we are in a list, close it.
            # This basic handling assumes simple list structures.
            if list_stack:
                while list_stack:
                    html_output += "</ol>\n"
                    list_stack.pop()
            # Non-list items are not processed further in this specific function.
            continue

        item_text = match.group(2).strip()
        # Determine the indentation level based on leading spaces in the original line
        indentation = len(original_line) - len(original_line.lstrip())
        level = indentation // 2  # Assuming 2 spaces for indentation

        if not list_stack:  # First item
            list_stack.append(level)
            # No need to add <ol> here, it's added at the start,
            # but if the first item is indented, it implies a nested structure from the beginning.
            # This part needs careful handling for lists that *start* indented without a parent.
            # For simplicity, we'll assume the first item defines the base level for *this* list segment.
            # If level > 0 for the first item, we add opening <ol> tags.
            for _ in range(level):
                html_output += "<ol>\n"


        elif level > list_stack[-1]:  # New nested list
            # If moving to a deeper level, add one <ol> for each increment in level.
            for _ in range(level - list_stack[-1]):
                html_output += "<ol>\n"
            list_stack.append(level)
        elif level < list_stack[-1]:  # Closing nested list(s)
            while list_stack and level < list_stack[-1]:
                html_output += "</ol>\n"
                list_stack.pop()
            # If after popping, the stack is empty or level doesn't match,
            # it implies a malformed structure or end of a list block.
            # This basic parser might not robustly handle all malformed cases.
            if not list_stack or level != list_stack[-1]:
                # This could indicate a break in list structure or malformed Markdown.
                # If stack is empty, and we have an item, start a new list.
                if not list_stack:
                    for _ in range(level + 1): # +1 because level is 0-indexed for nesting depth
                        html_output += "<ol>\n"
                    list_stack.append(level)

        html_output += f"  <li>{item_text}</li>\n"

    # Close any remaining open tags
    while list_stack:
        html_output += "</ol>\n"
        list_stack.pop()

    # Ensure the main list is closed if items were added.
    # If html_output is just "<ol>\n" and no items, it means empty input or no list items found.
    # A more direct check: if "<li>" is not in html_output.
    if "<li>" not in html_output:
        return ""

    # If the list stack was never populated (e.g. first item caused issues or was not list item),
    # but we have the initial "<ol>\n", we need to ensure it's handled.
    # The logic above tries to manage this, but as a safeguard:
    if html_output == "<ol>\n" and not list_stack and "<li>" not in html_output:
        return ""

    return html_output.strip()
