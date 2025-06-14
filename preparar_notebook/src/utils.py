import json
import pathlib

COUNTER = 0
LIMIT_COUNTER = 10

PORTAFOLIO_FOLDER = 'portafolio'    # portAfolio not portfolio

def ask_for_something(string, optionsTrue, optionsFalse):
    print(string, end=' ')
    answer = input()
    options = optionsTrue + optionsFalse
    while answer.lower() not in options:
        print(f"Please, write {optionsTrue} {optionsFalse}", end=' ')
        answer = input()
    if answer.lower() in optionsTrue:
        return True
    else:
        return False

def string_to_dict(notebook_content):
    try:
        filter_text = notebook_content.replace('```json', '').replace('\n', '').replace('```', '')
        json_content = json.loads(filter_text)
        dict_content = dict(json_content)
        return dict_content
    except Exception as e:
        print(f"Error converting string to dictionary: {e}")
        print(f"Input string: {notebook_content}")
        return {}

def get_portafolio_path(path):
    global COUNTER
    path = pathlib.Path(path)
    parent = path.parent
    last_folder = path.parts[-1]
    if last_folder == PORTAFOLIO_FOLDER:
        return pathlib.Path(path)
    else:
        if COUNTER < LIMIT_COUNTER:
            COUNTER += 1
            return get_portafolio_path(parent)
        else:
            raise Exception('Portafolio folder not found')

def get_pwd_path():
    return pathlib.Path().absolute()