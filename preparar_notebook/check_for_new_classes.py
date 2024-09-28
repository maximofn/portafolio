import argparse
import re

clases = [
    'ansi-blue-fg',
    'ansi-cyan-fg',
    'ansi-green-fg',
    'ansi-green-intense-fg ansi-bold',
    'ansi-red-fg',
    'bp',
    'c1',
    'fm',
    'k',
    'kc',
    'kn',
    'mf',
    'mi',
    'n',
    'nb',
    'nc',
    'nd',
    'ne',
    'nf',
    'nn',
    'o',
    'ow',
    'p',
    's1',
    's2',
    'sa',
    'sd',
    'se',
    'si',
    'vm',
    'w',
    'err',
]

def check_for_new_classes(path_file):
    class_name_list = []
    with open(path_file, "r") as file:
        for line in file:
            # Find all '<span class="X"' in the line and get the class name
            for class_name in re.findall(r'<span class="([^"]+)"', line):
                # Append the class name to the list
                class_name_list.append(class_name)

    # Convert the list to a set to remove duplicates
    class_name_set = set(class_name_list)
    class_name_set

    # Check if there are any new classes in class_name_set that are not in clases
    new_classes = []
    for class_name in class_name_set:
        if class_name not in clases:
            new_classes.append(class_name)

    if new_classes:
        print("""
              !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
              Se han encontrado nuevas clases en el notebook.
              Agrega las clases a los estilos de PostLayout.astro y a la lista de clases de check_for_new_classes.py
              !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

              New classes found:
              """)
        for new_class in new_classes:
            print("New class: ", new_class)
        exit(1)
    # else:
        # exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check for new classes in a html file')
    parser.add_argument('html', type=str, help='Path to the notebook')
    args = parser.parse_args()

    check_for_new_classes(args.html)