import argparse
import re

REPLACE = True
STOP_COUNTER = False

def remove_empty_lines(lines):
    lines_removed = False
    for number_reversed_line, line in enumerate(list(reversed(lines))):
        if '></CodeBlockOutputCell>' in line or '></CodeBlockInputCell>' in line:
            start_line = len(lines) - number_reversed_line - 1
            end_line = None
            # print(f"\nstart_line: {start_line} of {len(lines)}, line({start_line}): {lines[start_line]}")
            for i in range(start_line+1, len(lines)):
                if lines[i] != '':
                    end_line = i
                    break
            if end_line and (end_line-start_line>2):
                # print(f"end_line: {end_line} of {len(lines)}, line({end_line}): {lines[end_line]}, line({end_line+1}): {lines[end_line+1]}")
                # Remove items from start_line+1 to end_line-1
                for i in range(end_line-1, start_line, -1):
                    lines.pop(i)
                lines_removed = True
                break
            # else:
                # print(f"end_line: {end_line}")
    return lines, lines_removed

def remove_blank_spaces_at_the_beginning_of_code_lines(content):
    six_spaces = 6 * " "
    init_code_line = "'"
    wrong_code_line = six_spaces + init_code_line + six_spaces
    wrong_code_line = "      '      "
    for i, line in enumerate(content):
        if "<CodeBlockInputCell" in line:
            code_lines = line.split('\n')
            for j, code_line in enumerate(code_lines):
                if code_line.startswith(wrong_code_line):
                    code_lines[j] = code_line[0:7] + code_line[13:]
                    if code_lines[j] == "      '',":
                        code_lines[j] = "      ' ',"
            content[i] = '\n'.join(code_lines)
    return content

def format_input_code_block(section_content: str) -> str | None:
    """
    Formats input code blocks from HTML section content to CodeBlockInputCell format.
    Returns None if the section is not an input code block.

    Args:
        section_content (str): The content of the section to format.

    Returns:
        str | None: The formatted code block or None if the section is not an input code block.
    """
    # Check if this is NOT a code cell (markdown cells should return None)
    if 'section-block-markdown-cell' in section_content:
        return None
    
    # Check if this is an input code block
    if 'section-block-code-cell-' not in section_content or 'input-code' not in section_content:
        return None
    
    # Extract code content from <pre> tags
    pre_pattern = r'<pre[^>]*>(.*?)</pre>'
    pre_match = re.search(pre_pattern, section_content, re.DOTALL)
    
    if not pre_match:
        return None
    
    pre_content = pre_match.group(1)
    
    # Split into lines and clean up
    lines = pre_content.split('\n')
    code_lines = []
    
    for line in lines:
        # Remove leading and trailing whitespace, but preserve internal structure
        line = line.strip()
        if line:  # Only add non-empty lines
            # Don't escape quotes - keep them as they are in the original HTML
            code_lines.append(f"      '{line}',")
    
    # Build the formatted output with exact format matching the tests
    result = "      <CodeBlockInputCell\n"
    result += "        text={[\n"
    result += "\n".join(code_lines) + "\n"
    result += "        ]}\n"
    result += "        languaje='python'\n"
    result += "      ></CodeBlockInputCell>"
    
    return result

def format_output_code_block(section_content: str) -> str | None:
    """
    Formats output code blocks from HTML section content to CodeBlockOutputCell format.
    Returns None if the section is not an output code block.

    Args:
        section_content (str): The content of the section to format.

    Returns:
        str | None: The formatted code block or None if the section is not an output code block.
    """
    # Check if this is NOT a code cell (markdown cells should return None)
    if 'section-block-markdown-cell' in section_content:
        return None
    
    # Check if this is an output code block
    if 'section-block-code-cell-' not in section_content or 'output-wrapper' not in section_content:
        return None
    
    # Extract content from <pre> tags in output sections
    pre_pattern = r'<pre[^>]*>(.*?)</pre>'
    pre_match = re.search(pre_pattern, section_content, re.DOTALL)
    
    if not pre_match:
        return None
    
    pre_content = pre_match.group(1)
    
    # Split into lines and clean up
    lines = pre_content.split('\n')
    code_lines = []
    
    for line in lines:
        # Remove leading and trailing whitespace
        line = line.strip()
        if line:  # Only add non-empty lines
            # For output, we need to handle HTML entities and special formatting
            code_lines.append(f"          '{line}',")
    
    # Build the formatted output with exact format matching the tests
    result = "      <CodeBlockOutputCell\n"
    result += "        text={[\n"
    result += "\n".join(code_lines) + "\n"
    result += "        ]}\n"
    result += "        languaje='python'\n"
    result += "      ></CodeBlockOutputCell>"
    
    return result

def format_code_blocks(content: str) -> str:
    """
    Formats code blocks in a html file.

    Args:
        content (str): The content of the html file.

    Returns:
        str: The formatted html file.
    """

    # Get all lines
    lines = content.split('\n')

    # Iterate for each line
    num_lines = len(lines)
    for i, line in enumerate(lines):
        section_start_line = None
        section_end_line = None
        section_content = ""
        input_code_block = None
        output_code_block = None
        # Check if the line contains '<section>'
        if '<section' in line:
            # Look for '</section>'
            for j in range(i+1, num_lines):
                if '</section>' in lines[j]:
                    section_start_line = i
                    section_end_line = j
                    break
            # Get the content of the section
            if section_start_line and section_end_line:
                for k in range(section_start_line, section_end_line+1):
                    section_content += lines[k] + '\n'
                    section_content
                input_code_block = format_input_code_block(section_content)
                output_code_block = format_output_code_block(section_content)

        # Replace the section with the formatted section
        if input_code_block:
            lines[section_start_line] = input_code_block
        if output_code_block:
            lines[section_start_line] = output_code_block

        # Change the rest of the lines to be empty
        if input_code_block or output_code_block:
            for k in range(section_start_line+1, section_end_line+1):
                lines[k] = ''
    
    # Remove empty lines
    need_remove_empty_lines = True
    while need_remove_empty_lines:
        lines, lines_removed = remove_empty_lines(lines)
        if not lines_removed:
            need_remove_empty_lines = False
    
    # Remove blank spaces at the beginning of the lines
    lines = remove_blank_spaces_at_the_beginning_of_code_lines(lines)

    html_content = '\n'.join(lines)
    return html_content

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Format code blocks in a html file')
    parser.add_argument('html', type=str, help='Path to the html file')
    args = parser.parse_args()

    format_code_blocks(args.html)