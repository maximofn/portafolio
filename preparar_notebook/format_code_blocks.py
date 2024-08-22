import argparse

REPLACE = False
STOP_COUNTER = False

start_input_code_block = """<CodeBlockInputCell
  text={["""
start_output_code_block = """<CodeBlockOutputCell
  text={["""
end_input_code_block = """  ]}
  languaje='python'
></CodeBlockInputCell>"""
end_output_code_block = """  ]}
  languaje='python'
></CodeBlockOutputCell>"""


def format_code_blocks(path_file):
    # read file
    with open(path_file, "r") as file:
        content = file.read()

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
                        while not lines[j].startswith('</pre>'):
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
                                            if lines[j+6].startswith('<pre>'):
                                                # Add the rest of the line to the code list
                                                code_to_append = lines[j+6][5:]
                                                code_to_append = code_to_append.replace("'", "\\'")
                                                code_to_append = "    '" + code_to_append + "',"
                                                output_cell_code.append(code_to_append)

                                                # If this line contains '</pre>', remove to de code list
                                                if '</pre>' in lines[j+6]:
                                                    k = j+6
                                                    output_cell_code[0] = output_cell_code[0].replace("</pre>", "")
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
                                                        lines[i] = lines[i] + '\n' + input_cell_code[pos]
                                                    lines[i] = lines[i] + '\n' + end_input_code_block
                                                    lines[i] = lines[i] + '\n' + start_output_code_block
                                                    for pos in range(len(output_cell_code)):
                                                        lines[i] = lines[i] + '\n' + output_cell_code[pos]
                                                    lines[i] = lines[i] + '\n' + end_output_code_block

                                                    if REPLACE:
                                                        print("!"*100)
                                                        print(f"i: {i}")
                                                        print(f"j: {j}")
                                                        print(f"k: {k}")
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
                                for k in range(len(input_cell_code)):
                                    lines[i] = lines[i] + '\n' + input_cell_code[k]
                                lines[i] = lines[i] + '\n' + end_input_code_block
                                
                                if REPLACE:
                                    for pos in range(i+1, j+1):
                                        print(f"lines[{i}]: {lines[i]}")
                                        lines[pos] = ''
                                        print(f"\tlines[{i}]: {lines[i]}")
                                else:
                                    lines[i] = lines[i] + '\n' + line_i



                                
    
    # Write the formatted content to the file
    with open(path_file, "w") as file:
        file.write('\n'.join(lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Format code blocks in a html file')
    parser.add_argument('html', type=str, help='Path to the html file')
    args = parser.parse_args()

    format_code_blocks(args.html)