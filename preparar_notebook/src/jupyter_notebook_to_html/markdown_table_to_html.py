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
        """Convert inline code (`code`) to HTML format only for command-like code"""
        # Pattern to match text between backticks
        pattern = r'`([^`]+)`'
        
        def replace_code(match):
            code_content = match.group(1)
            # Only convert to HTML if it looks like a command (contains spaces and command keywords)
            command_keywords = ['pip', 'docker', 'apt', 'npm', 'yarn', 'conda', 'git', 'sudo', 'curl', 'wget', 'uv']
            has_spaces = ' ' in code_content
            has_command_keyword = any(keyword in code_content.lower() for keyword in command_keywords)
            
            if has_spaces and has_command_keyword:
                # Escape HTML characters
                escaped_content = code_content.replace('<', '&#x3C;').replace('>', '&#x3E;')
                return f'<code>{escaped_content}</code>'
            else:
                # Return original markdown for simple code
                return f'`{code_content}`'
        
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
