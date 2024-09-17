
def ask_for_something(string, optionsTrue, optionsFalse):
    print(string, end=' ')
    answer = input()
    while answer.lower() not in options:
        print(f"Please, write {optionsTrue} {optionsFalse}", end=' ')
        answer = input()
    if answer.lower() in optionsTrue:
        return True
    else:
        return False