import re

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
    """
    lines = markdown_text.strip().split('\n')
    html_lines = []
    list_level_markers = {}  # Stores the type of list marker ('ul' or 'ol') at each level

    def get_indent_level(line_text):
        # More robust way to count leading spaces
        leading_spaces = 0
        for char in line_text:
            if char == ' ':
                leading_spaces += 1
            else:
                break
        return leading_spaces // 2

    def close_lists(current_level):
        closed_html = ""
        levels_to_close = sorted([lvl for lvl in list_level_markers if lvl > current_level], reverse=True)
        for lvl in levels_to_close:
            if list_level_markers[lvl] == 'ul':
                closed_html += "  " * lvl + "</ul>\n"
            del list_level_markers[lvl]
        return closed_html

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        indent_level = get_indent_level(line)
        is_unordered_list_item = stripped_line.startswith(('-', '*', '+')) and stripped_line[1:2] == ' '

        if is_unordered_list_item:
            # Ensure content is stripped of leading/trailing whitespace from the original line part
            item_content = line.strip()[2:].strip() # Strip the content itself

            # Close deeper lists if current item is at a shallower level
            html_lines.append(close_lists(indent_level))

            if indent_level not in list_level_markers:
                # Start a new list
                list_level_markers[indent_level] = 'ul'
                # Corrected: The <ul> tag should also be indented according to its level
                html_lines.append("  " * indent_level + "<ul>\n")

            # Corrected: The <li> tag should be indented one level deeper than its <ul>
            html_lines.append("  " * (indent_level + 1) + f"<li>{item_content}</li>\n")
        else:
            # Non-list item, close all open lists
            html_lines.append(close_lists(-1)) # Close all lists
            # We'll just append non-list lines as paragraphs for simplicity,
            # though the request is focused on list conversion.
            html_lines.append(f"<p>{stripped_line}</p>\n")


    # Close any remaining open lists at the end
    html_lines.append(close_lists(-1))

    return "".join(html_lines).strip()
