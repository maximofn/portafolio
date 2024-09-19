import json

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
    filter_text = notebook_content.replace('```json', '').replace('\n', '').replace('```', '')
    json_content = json.loads(filter_text)
    dict_content = dict(json_content)
    return dict_content