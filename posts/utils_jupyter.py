import json
import re

DEBUG = False

def open_notebook_to_read(filename):
    try:
        with open(filename, 'r') as f:
            notebook = json.load(f)
    except FileNotFoundError:
        print(f"El archivo {filename} no se encontró")
        return None
    except PermissionError:
        print(f"No se tienen permisos de lectura para el archivo {filename}")
        return None
    except json.JSONDecodeError:
        print(f"El archivo {filename} no tiene el formato JSON correcto")
        return None
    return notebook

def get_headers(cells):
    headers = []
    for cell in cells:
        try:
            if cell['cell_type'] == 'markdown' and cell['source'][0].startswith('#'):
                headers.append(cell['source'][0])
        except TypeError:
            print(f"El elemento {cell} de la lista cells no es un diccionario")
        except KeyError:
            print(f"El diccionario {cell} no tiene la clave 'cell_type' o 'source'")
    return headers




def get_notebook_as_dict(filename):
    with open(filename, 'r') as f:
        notebook = json.load(f)
    return notebook

def open_notebook(filename, type="w"):
    return open(f"{filename}", type)

def close_notebook(file):
    file.close()

def get_headers(cells):
    headers = []
    for cell in cells:
        if cell['cell_type'] == 'markdown' and cell['source'][0].startswith('#'):
            headers.append(cell['source'][0])
    return headers

def write_end_of_line(file, i, N):
    if i == N-1:
        string = "\n"
        file.write(string)
        if DEBUG: print(string, end='')
    else:
        string = ",\n"
        file.write(string)
        if DEBUG: print(string, end='')

def write_dict_to_file(file, dictionary, indentation):
    if len(dictionary) > 0:
        string = "{\n"
        file.write(string)
        if DEBUG: print(string, end='')
        indentation += 1
        for i, key in enumerate(dictionary.keys()):
            string = ((" ")*2*indentation)+f"\"{key}\": "
            file.write(string)
            if DEBUG: print(string, end='')
            if type(dictionary[key]) == dict:
                write_dict_to_file(file, dictionary[key], indentation)
            elif type(dictionary[key]) == list:
                write_list_to_file(file, dictionary[key], indentation)
            elif type(dictionary[key]) == str:
                write_str_to_file(file, dictionary[key], indentation)
            elif type(dictionary[key]) == int:
                write_int_to_file(file, dictionary[key], indentation)
            elif type(dictionary[key]) == bool:
                write_bool_to_file(file, dictionary[key], indentation)
            else:
                write_rest_to_file(file, dictionary[key], indentation)
            write_end_of_line(file, i, len(dictionary.keys()))
        indentation -= 1
        string = ((" ")*2*indentation)+"}"
        file.write(string)
        if DEBUG: print(string, end='')
    else:
        string = "{}"
        file.write(string)
        if DEBUG: print(string, end='')
    return indentation

def write_list_to_file(file, list, indentation):
    if len(list) > 0:
        string = "[\n"+((" ")*2*indentation)
        file.write(string)
        if DEBUG: print(string, end='')
        indentation += 1
        for i, item in enumerate(list):
            if type(item) == dict:
                write_dict_to_file(file, item, indentation)
            elif type(item) == list:
                write_list_to_file(file, item, indentation)
            elif type(item) == str:
                write_str_to_file(file, item, indentation)
            elif type(item) == int:
                write_int_to_file(file, item, indentation)
            elif type(item) == bool:
                write_bool_to_file(file, item, indentation)
            else:
                write_rest_to_file(file, item, indentation)
            write_end_of_line(file, i, len(list))
        indentation -= 1
        string = ((" ")*2*indentation)+"]"
        file.write(string)
        if DEBUG: print(string, end='')
    else:
        string = "[]"
        file.write(string)
        if DEBUG: print(string, end='')
    return indentation

def write_str_to_file(file, string, indentation):
    minidebug = False
    if type(string) == int:
        string = str(string)
    # if "[0;31m--------------" in string:
        # minidebug = True
    if minidebug: print(f"minidebug raw: {string}")
    string = re.sub(r'\\', r'\\\\', string) # Replace \ with \\
    string = re.sub('"', '\\"', string) # Remplace " by \"
    string = re.sub(r'\n', r'\\n', string)  # Remplace \n by \ character + n character
    string = re.sub(r'\t', r'\\t', string)  # Remplace \t by \ character + t character
    string = re.sub(r'\x1b', r'\\u001b', string)    # Remplace escape character (27) by \\u001b
    if minidebug: print(f"minidebug: {string}")
    if minidebug: print(f"first char: {string[0]}, int: {ord(string[0])}")
    string = f"\"{string}\""
    if minidebug: print()
    file.write(string)
    if DEBUG: print(string, end='')
    return indentation

def write_int_to_file(file, i, indentation):
    string = f"{i}"
    file.write(string)
    if DEBUG: print(string, end='')
    return indentation

def write_bool_to_file(file, b, indentation):
    string = str(b).lower()
    file.write(string)
    if DEBUG: print(string, end='')
    return indentation

def write_rest_to_file(file, rest, indentation):
    string = f"\"{rest}\""
    file.write(string)
    if DEBUG: print(string, end='')
    return indentation

def dict_to_ipynb(notebook, filename):
    new_notebook = open_notebook(filename)

    indentation = 0
    string = ((" ")*2*indentation)+"{\n"
    new_notebook.write(string)
    if DEBUG: print(string, end='')
    indentation += 1

    notebook_keys = list(notebook.keys())
    for k, key in enumerate(notebook_keys):
        if type(notebook[key]) == dict:
            string = ((" ")*2*indentation)+"\""+key+"\": "
            new_notebook.write(string)
            if DEBUG: print(string, end='')
            indentation = write_dict_to_file(new_notebook, notebook[key], indentation)
            write_end_of_line(new_notebook, k, len(notebook_keys))
        elif type(notebook[key]) == list:
            string = ((" ")*2*indentation)+"\""+key+"\": "
            new_notebook.write(string)
            if DEBUG: print(string, end='')
            indentation = write_list_to_file(new_notebook, notebook[key], indentation)
            write_end_of_line(new_notebook, k, len(notebook_keys))
        elif type(notebook[key] == int):
            string = ((" ")*2*indentation)+"\""+key+"\": "
            new_notebook.write(string)
            if DEBUG: print(string, end='')
            indentation = write_int_to_file(new_notebook, notebook[key], indentation)
            write_end_of_line(new_notebook, k, len(notebook_keys))
        elif type(notebook[key] == str):
            string = ((" ")*2*indentation)+"\""+key+"\": "
            new_notebook.write(string)
            if DEBUG: print(string, end='')
            indentation = write_str_to_file(new_notebook, notebook[key], indentation)
            write_end_of_line(new_notebook, k, len(notebook_keys))
        else:
            string = ((" ")*2*indentation)+"\""+key+"\": "
            new_notebook.write(string)
            if DEBUG: print(string, end='')
            indentation = write_rest_to_file(new_notebook, notebook[key], indentation)
            write_end_of_line(new_notebook, k, len(notebook_keys))
    indentation -= 1
    string = ((" ")*2*indentation)+"}\n"
    new_notebook.write(string)
    if DEBUG: print(string, end='')

    close_notebook(new_notebook)