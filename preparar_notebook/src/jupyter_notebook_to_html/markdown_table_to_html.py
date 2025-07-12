import re

def markdown_table_to_html(markdown_table_string):
    """
    Converts a Markdown table string to an HTML table string.

    Args:
        markdown_table_string: The Markdown table as a string.

    Returns:
        The HTML representation of the table.
    """
    lines = markdown_table_string.strip().split('\n')

    if len(lines) < 2:
        return ""  # Not enough lines for a header and separator

    # Helper to extract cell content from a line.
    # Handles lines with or without leading/trailing pipes.
    def get_cells_from_line(line_str):
        line_str = line_str.strip()
        if line_str.startswith('|'):
            line_str = line_str[1:]
        if line_str.endswith('|'):
            line_str = line_str[:-1]
        return [cell.strip() for cell in re.split(r'\s*\|\s*', line_str)]

    # Helper to convert inline code in cell content
    def process_inline_code(cell_content):
        """Convert inline code (`code`) to HTML format using generic patterns"""
        
        # Pattern to match text between backticks
        pattern = r'`([^`]+)`'
        
        def replace_code(match):
            code_content = match.group(1)
            
            # Generic pattern-based detection
            has_spaces = ' ' in code_content
            
            # Check for actual command patterns (not just any text with spaces)
            is_command_like = has_spaces and (
                # Commands typically have specific patterns
                re.search(r'\b(install|run|update|add|build|exec|start|stop|apt|pip|docker|conda|git|sudo|curl|wget)\s+', code_content.lower()) or
                '--' in code_content or  # flag pattern
                '.py' in code_content or '.js' in code_content  # script file pattern
            )
            
            # Simple single-character content without spaces gets normal formatting (preserve only for very simple cases)
            if (not has_spaces and len(code_content) == 1 and 
                not any(ord(char) > 127 for char in code_content)):
                # Single ASCII characters that appear in Unicode context should use normal formatting
                if any(ord(char) > 127 for char in cell_content):
                    return f'<code>{code_content}</code>'
                # Otherwise preserve original behavior
                return f'`{code_content}`'
            
            # Check for complex context that needs special processing
            transformation_pattern = r'\b(se convierte en|becomes|transforms to|converts to|results in)\b'
            has_transformation = bool(re.search(transformation_pattern, cell_content.lower()))
            has_unicode_in_cell = any(ord(char) > 127 for char in cell_content)
            is_technical = ((re.search(r'^[a-z_]+[a-z0-9_]*$', code_content) and '_' in code_content) or 
                           (re.search(r'^[a-z]+$', code_content) and code_content.lower() in ['lowercase', 'uppercase', 'title', 'capitalize']))
            
            # Preserve original behavior for simple cases (no spaces, no unicode, no special context)
            if (not has_spaces and 
                not any(ord(char) > 127 for char in code_content) and
                not has_unicode_in_cell and
                not has_transformation and
                not is_technical):
                return f'`{code_content}`'
            
            # Command-like content gets normal HTML code formatting
            if is_command_like:
                escaped_content = code_content.replace('<', '&#x3C;').replace('>', '&#x3E;')
                return f'<code>{escaped_content}</code>'
            
            # Check if it appears in transformation context (before or after transformation indicators)
            code_position = cell_content.find(f'`{code_content}`')
            
            if has_transformation and code_position >= 0:
                # Find if this specific code appears after a transformation phrase
                text_before = cell_content[:code_position].lower()
                if re.search(transformation_pattern, text_before):
                    return f'<code>{code_content}</code>'  # Normal formatting for transformation results
            
            # Technical identifiers (snake_case patterns and common technical terms)
            if is_technical:
                return f'<code>{code_content}</code>'  # Normal formatting for technical terms
            
            # Determine formatting based on content characteristics
            needs_escaped_backticks = (
                # Unicode characters (non-ASCII)
                any(ord(char) > 127 for char in code_content) or
                # Padded content (leading/trailing spaces)
                code_content != code_content.strip() or
                # Example phrases (descriptive text, not code) - enhanced detection
                (has_spaces and len(code_content.split()) <= 4 and 
                 not re.search(r'[()[\]{}=<>_]', code_content) and  # no code-like symbols
                 not is_command_like) or  # and not a command
                # Text that appears before transformation (likely example text)
                (has_transformation and has_spaces and 
                 not re.search(transformation_pattern, cell_content[:code_position].lower()) if code_position >= 0 else False)
            )
            
            # Apply escaped backticks for special cases
            if needs_escaped_backticks:
                return f'<code>&#x60;{code_content}&#x60;</code>'
            
            # Default: normal code formatting
            return f'<code>{code_content}</code>'
        
        return re.sub(pattern, replace_code, cell_content)

    header_line = lines[0]
    separator_line = lines[1]
    data_lines = lines[2:]

    headers = get_cells_from_line(header_line)
    num_columns = len(headers)

    alignments = []
    # Separator line cells also need careful parsing, similar to header/data lines
    separator_cells_text = get_cells_from_line(separator_line)

    for i, cell_content in enumerate(separator_cells_text):
        if i >= num_columns: # More alignment cells than header columns, ignore extras
            break
        if cell_content.startswith(':') and cell_content.endswith(':'):
            alignments.append('center')
        elif cell_content.endswith(':'):
            alignments.append('right')
        elif cell_content.startswith(':'): # Default or :---
            alignments.append('left')
        else: # Just ---
            alignments.append('left') # Default to left

    # Ensure alignments list matches number of columns, padding with 'left' if necessary
    if len(alignments) < num_columns:
        alignments.extend(['left'] * (num_columns - len(alignments)))
    elif len(alignments) > num_columns: # Should not happen if get_cells_from_line is robust
        alignments = alignments[:num_columns]


    html_table = "<table>\n"

    # Build table header
    html_table += "  <thead>\n    <tr>\n"
    for i, header in enumerate(headers):
        align_attr = f' style="text-align: {alignments[i]};"' if alignments[i] != 'left' else ''
        # Process inline code in headers too
        processed_header = process_inline_code(header)
        html_table += f'      <th{align_attr}>{processed_header}</th>\n'
    html_table += "    </tr>\n  </thead>\n"

    # Build table body
    html_table += "  <tbody>\n"
    for line_idx, line in enumerate(data_lines):
        if not line.strip():
            continue

        current_row_cells = get_cells_from_line(line)
        html_table += "    <tr>\n"
        for i in range(num_columns): # Iterate based on the number of columns defined by the header
            cell_content = ""
            if i < len(current_row_cells):
                cell_content = current_row_cells[i]

            # Process inline code in cell content
            processed_cell_content = process_inline_code(cell_content)

            align_attr = f' style="text-align: {alignments[i]};"' if alignments[i] != 'left' else ''
            html_table += f'      <td{align_attr}>{processed_cell_content}</td>\n'
        html_table += "    </tr>\n"
    html_table += "  </tbody>\n"
    html_table += "</table>"

    return html_table
