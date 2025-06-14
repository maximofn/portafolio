import re

def generic_markdown_to_list_specific_markdowns(markdown_content: str) -> list[str]:
    if not markdown_content.strip():
        return []

    # Regex for different markdown blocks
    # Code block: ```lang\ncode\n```. The block itself does not end with a newline after ``` in the list.
    code_block_regex = r'^```(?:[a-zA-Z0-9_.-]*)?\n[\s\S]*?^```' # Matched block ends with ```

    # List item line regex (used iteratively)
    # Starts with marker or is indented continuation.
    # A list item can span multiple lines if subsequent lines are indented.
    # This regex is for a single line that could be part of a list.
    list_line_pattern = r'^(?:[ \t]*(?:[-*+]|\d+\.)[ \t]+.*|[ \t]+.*)(?:\n|$)'
    list_start_pattern = r'^[ \t]*(?:[-*+]|\d+\.)[ \t]+'

    # Table line regex (used iteratively)
    # A line that is part of a table (contains pipes).
    table_line_pattern = r'^[ \t]*\|.*\|[ \t]*(?:\n|$)'
    table_start_pattern = r'^[ \t]*\|.*\|'


    def transform_links_in_text(text_block):
        # Transform specific internal links. External links and image links remain unchanged.
        text_block = re.sub(r'https://www.maximofn.com/blog', '/blog', text_block)
        text_block = re.sub(r'https://www.maximofn.com/(en|pt-br)/blog/', r'/\1/blog/', text_block)
        return text_block

    blocks = []
    # Preserve leading spaces on the first content line, but strip leading/trailing newlines and trailing spaces.
    remaining_content = markdown_content.lstrip('\n').rstrip()

    while remaining_content:
        # 1. Try to match Code Block
        code_match = re.match(code_block_regex, remaining_content, re.MULTILINE)
        if code_match:
            block_content = code_match.group(0)
            blocks.append(block_content) # Code blocks are not link-transformed
            remaining_content = remaining_content[len(block_content):].lstrip('\n')
            continue

        # 2. Try to match List Block
        first_line_of_remaining = remaining_content.split('\n', 1)[0]
        if re.match(list_start_pattern, first_line_of_remaining):
            full_list_content = ""
            temp_list_remaining = remaining_content
            is_first_list_line = True
            while temp_list_remaining:
                # For the first line, it must match the start pattern
                if is_first_list_line:
                    if not re.match(list_start_pattern, temp_list_remaining.split('\n',1)[0]):
                        break
                # For subsequent lines, they must either be list items or indented
                elif not (re.match(list_start_pattern, temp_list_remaining.split('\n',1)[0]) or \
                          re.match(r'^[ \t]+(?=\S)', temp_list_remaining.split('\n',1)[0])): # Indented and not blank
                    break

                # Greedily consume lines that are part of the list.
                # A line is part of the list if it starts with a list marker or is indented continuation.
                # A blank line would break the list unless it's an indented blank line (part of item).
                # Simpler: take lines as long as they match list_start_pattern or are indented continuations.
                # The regex list_line_pattern is too broad here. Let's refine.

                current_line_is_list_item = bool(re.match(list_start_pattern, temp_list_remaining.split('\n',1)[0]))
                current_line_is_indented = bool(re.match(r'^[ \t]+(?=\S)', temp_list_remaining.split('\n',1)[0]))

                if is_first_list_line and not current_line_is_list_item:
                    break # First line must be a list item starter
                if not is_first_list_line and not current_line_is_list_item and not current_line_is_indented:
                    # If not first line, and not a new item, and not indented, then list ends.
                    # Exception: if it's a blank line within an item (e.g. indented blank line), it could continue.
                    # For now, any non-indented, non-item line breaks the list.
                    # A blank line (not indented) also breaks the list.
                    if not temp_list_remaining.split('\n',1)[0].strip(): # It's a blank line
                        break # Blank line breaks list block here
                    break


                # Consume one line
                line_end_pos = temp_list_remaining.find('\n')
                if line_end_pos == -1: # Last line
                    line = temp_list_remaining
                    temp_list_remaining = ""
                else:
                    line = temp_list_remaining[:line_end_pos+1]
                    temp_list_remaining = temp_list_remaining[line_end_pos+1:]

                full_list_content += line
                is_first_list_line = False

            if full_list_content:
                full_list_content = full_list_content.rstrip('\n') + '\n' # Ensure single trailing newline
                blocks.append(transform_links_in_text(full_list_content))
                remaining_content = remaining_content[len(full_list_content):].lstrip('\n')
                continue

        # 3. Try to match Table Block
        if re.match(table_start_pattern, first_line_of_remaining):
            full_table_content = ""
            temp_table_remaining = remaining_content
            while temp_table_remaining:
                if not re.match(table_start_pattern, temp_table_remaining.split('\n',1)[0]):
                    break # Line doesn't look like a table row an Lymore

                line_end_pos = temp_table_remaining.find('\n')
                if line_end_pos == -1:
                    line = temp_table_remaining
                    temp_table_remaining = ""
                else:
                    line = temp_table_remaining[:line_end_pos+1]
                    temp_table_remaining = temp_table_remaining[line_end_pos+1:]
                full_table_content += line

            if full_table_content:
                # Preserve the trailing newline status of the original table block.
                # full_table_content is the raw block extracted from input.
                processed_table_content = full_table_content.rstrip('\n') # Normalize: remove any existing trailing newlines

                if full_table_content.endswith('\n'): # Check if the original raw block ended with a newline
                    processed_table_content += '\n'   # If so, add a single newline back.

                blocks.append(transform_links_in_text(processed_table_content))
                # Consume the length of the original full_table_content from remaining_content
                remaining_content = remaining_content[len(full_table_content):].lstrip('\n')
                continue

        # 4. If none of the above, it's a text/paragraph block.
        next_block_boundary = len(remaining_content)
        double_newline_match = re.search(r'\n\s*\n', remaining_content)
        if double_newline_match:
            next_block_boundary = min(next_block_boundary, double_newline_match.start())

        # Check for start of other block types on subsequent lines
        # Must search on remaining_content, not just one line
        # Start search from index 1 to avoid matching current line if it's not separated by \n\n

        # Find first occurrence of a special block start *not at pos 0*
        # (because pos 0 is handled by main loop's direct tentatives)
        searches = {
            'code': re.search(r'^```', remaining_content, re.MULTILINE),
            'list': re.search(list_start_pattern, remaining_content, re.MULTILINE),
            'table': re.search(table_start_pattern, remaining_content, re.MULTILINE)
        }

        for block_type, match_obj in searches.items():
            if match_obj and match_obj.start() > 0: # If found and not at the very beginning
                next_block_boundary = min(next_block_boundary, match_obj.start())
            # If match_obj.start() == 0, it means current text block is empty and next block starts immediately.
            # This case should be handled by lstrip('\n') and main loop.
            # However, if next_block_boundary is still len(remaining_content) or from \n\n,
            # and a special block starts at pos 0 of remaining_content, then this text block is empty.

        # If a special block starts at the very beginning of remaining_content, current_block_text should be empty.
        if next_block_boundary == 0 and (searches['code'] and searches['code'].start() == 0 or \
                                         searches['list'] and searches['list'].start() == 0 or \
                                         searches['table'] and searches['table'].start() == 0 ) :
             current_block_text = "" # Special block starts immediately.
        else:
            current_block_text = remaining_content[:next_block_boundary].strip()

        if current_block_text:
            blocks.append(transform_links_in_text(current_block_text))

        remaining_content = remaining_content[next_block_boundary:].lstrip('\n')

        if not remaining_content.strip():
            break

    return [b for b in blocks if b]
