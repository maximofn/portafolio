import argparse

REPLACE = True
STOP_COUNTER = False

start_input_code_block = """      <CodeBlockInputCell
        text={["""
start_output_code_block = """      <CodeBlockOutputCell
        text={["""
end_input_code_block = """        ]}
        languaje='python'
      ></CodeBlockInputCell>"""
end_output_code_block = """        ]}
        languaje='python'
      ></CodeBlockOutputCell>"""

def remove_empty_lines(lines):
    lines_removed = False
    for number_reversed_line, line in enumerate(list(reversed(lines))):
        if '></CodeBlockOutputCell>' in line:
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

def format_code_blocks(content):
    # Get all lines
    lines = content.split('\n')

    # Iterate for each line
    input_cell_code = []
    output_cell_code = []
    if STOP_COUNTER: cont = 0
    for i, line in enumerate(lines):
        # Check if the line contains '<section class="section-block-code-cell-">'
        if '<section class="section-block-code-cell-">' in line:
            # Check if the next line contains '<div class="input-code">'
            if '<div class="input-code">' in lines[i+1]:
                # Check if the next line contains '<div class="highlight hl-ipython3">'
                if '<div class="highlight hl-ipython3">' in lines[i+2]:
                    # Check if the next line starts with '<pre>'
                    if lines[i+3].startswith('<pre>'):
                        # Add the rest of the line to the code list
                        code_to_append = lines[i+3][5:]
                        code_to_append = code_to_append.replace("'", "\\'")
                        code_to_append = "    '" + code_to_append + "',"
                        input_cell_code.append(code_to_append)
                        #  While next lines don't start '</pre>', add them to the code list
                        j = i+4
                        while not '</pre>' in lines[j]:
                            code_to_append = lines[j]
                            code_to_append = code_to_append.replace("'", "\\'")
                            code_to_append = "    '" + code_to_append + "',"
                            input_cell_code.append(code_to_append)
                            j += 1
                        # Check if the line j+1 contains '</div>'
                        if '</div>' in lines[j+1]:
                            # Check if the line j+2 contains '<div class="output-wrapper">'
                            if '<div class="output-wrapper">' in lines[j+2]:
                                # Check if the next line contains '<div class="output-area">'
                                if '<div class="output-area">' in lines[j+3]:
                                    # Check if the next line contains '<div class="prompt'
                                    if '<div class="prompt' in lines[j+4]:
                                        # Check if the next line contains '<div class="output'
                                        if '<div class="output' in lines[j+5]:
                                            # Check if the next line starts with '<pre>'
                                            if '<pre>' in lines[j+6]:
                                                # Add the rest of the line to the code list
                                                code_to_append = lines[j+6][5:]
                                                code_to_append = code_to_append.replace("'", "\\'")
                                                code_to_append = "    '" + code_to_append + "',"
                                                output_cell_code.append(code_to_append)

                                                # If this line contains '</pre>', remove to de code list
                                                if '</pre>' in lines[j+6]:
                                                    k = j+6
                                                    output_cell_code[0] = output_cell_code[0].replace("</pre>", "").replace(" <pre>", "")
                                                else: # If this line not contains '</pre>', add the next lines to the code list
                                                    #  While next lines don't start '</pre>', add them to the code list
                                                    k = j+7
                                                    while not lines[k].startswith('</pre>'):
                                                        if lines[k].endswith('</pre>'):
                                                            code_to_append = lines[k][:-6]
                                                            end_while = True
                                                        else:
                                                            code_to_append = lines[k]
                                                            end_while = False
                                                        code_to_append = code_to_append.replace("'", "\\'")
                                                        code_to_append = "    '" + code_to_append + "',"
                                                        output_cell_code.append(code_to_append)
                                                        if end_while:
                                                            break
                                                        k += 1
                                                # Check if the lines k+1, k+2, k+3 contains '</div>'
                                                if ('</div>' in lines[k+1]) and ('</div>' in lines[k+2]) and ('</div>' in lines[k+3]):

                                                    # Insert the formatted code blockbefore the line 0
                                                    line_i = lines[i]
                                                    lines[i] = start_input_code_block
                                                    for pos in range(len(input_cell_code)):
                                                        # Get position of first ' character
                                                        for char_pos, char in enumerate(input_cell_code[pos]):
                                                            if char == "'":
                                                                start_position_character = char_pos
                                                                break
                                                        # Get position of last , character
                                                        for char_pos, char in enumerate(input_cell_code[pos][::-1]):
                                                            if char == ",":
                                                                end_position_character = len(input_cell_code[pos]) - char_pos
                                                                break
                                                        input_cell_code[pos] = input_cell_code[pos][start_position_character:end_position_character]
                                                        # Remove the first 6 spaces from pos+1 to the end
                                                        if pos > 0:
                                                            input_cell_code[pos] = input_cell_code[pos][0] + input_cell_code[pos][7:]
                                                        lines[i] = lines[i] + '\n          ' + input_cell_code[pos]
                                                    lines[i] = lines[i] + '\n' + end_input_code_block
                                                    lines[i] = lines[i] + '\n' + start_output_code_block
                                                    for pos in range(len(output_cell_code)):
                                                        # Get position of first ' character
                                                        for char_pos, char in enumerate(output_cell_code[pos]):
                                                            if char == "'":
                                                                start_position_character = char_pos
                                                                break
                                                        # Get position of last , character
                                                        for char_pos, char in enumerate(output_cell_code[pos][::-1]):
                                                            if char == ",":
                                                                end_position_character = len(output_cell_code[pos]) - char_pos
                                                                break
                                                        output_cell_code[pos] = output_cell_code[pos][start_position_character:end_position_character]
                                                        # Remove the first 6 spaces from pos+1 to the end
                                                        if pos > 0:
                                                            output_cell_code[pos] = output_cell_code[pos][0] + output_cell_code[pos][7:]
                                                        output_cell_code[pos] = output_cell_code[pos].replace("</pre>", "").replace(" <pre>", "")
                                                        # Check if the line contains only comments
                                                        if not (output_cell_code[pos][0]=="'" and output_cell_code[pos][1]=="'"):
                                                            lines[i] = lines[i] + '\n          ' + output_cell_code[pos]
                                                    lines[i] = lines[i] + '\n' + end_output_code_block

                                                    if REPLACE:
                                                        for pos in range(i+1, k+5):
                                                            lines[pos] = ''
                                                    else:
                                                        lines[i] = lines[i] + '\n' + line_i

                                                    # Clear the code list
                                                    input_cell_code = []
                                                    output_cell_code = []
                                                    if STOP_COUNTER:
                                                        if cont == 1:
                                                            break
                                                        cont += 1
                            else:
                                # Insert the formatted code blockbefore the line 0
                                line_i = lines[i]
                                lines[i] = start_input_code_block
                                for pos in range(len(input_cell_code)):
                                    lines[i] = lines[i] + '\n  ' + input_cell_code[pos]
                                lines[i] = lines[i] + '\n' + end_input_code_block
                                
                                if REPLACE:
                                    for pos in range(i+1, j+3):
                                        lines[pos] = ''
                                else:
                                    lines[i] = lines[i] + '\n' + line_i
    
    # Remove empty lines
    need_remove_empty_lines = True
    # counter = 0
    # limit_counter = 3
    while need_remove_empty_lines:
        # print(f"\nIteration: {counter}")
        lines, lines_removed = remove_empty_lines(lines)
        # counter += 1
        if not lines_removed:
            need_remove_empty_lines = False
        # if counter == limit_counter:
        #     break
    
    html_content = '\n'.join(lines)
    return html_content

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Format code blocks in a html file')
    parser.add_argument('html', type=str, help='Path to the html file')
    args = parser.parse_args()

    format_code_blocks(args.html)