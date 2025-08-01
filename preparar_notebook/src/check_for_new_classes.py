import argparse
import re

clases = [
    'ansi-blue-fg',
    'ansi-cyan-fg',
    'ansi-green-fg',
    'ansi-green-intense-fg ansi-bold',
    'ansi-red-fg',
    'ansi-red-intense-fg ansi-bold',
    'ansi-default-inverse-fg ansi-default-inverse-bg',
    'ansi-yellow-fg',
    'ansi-yellow-intense-fg ansi-bold',
    'ansi-white-fg',
    'ansi-red-intense-fg',
    'ansi-blue-intense-fg ansi-bold',
    'ansi-bold',
    'ansi-cyan-intense-fg ansi-bold',
    'ansi-magenta-fg',
    'ansi-magenta-intense-fg ansi-bold',
    'ansi-black-intense-fg',
    'ansi-yellow-bg',
    'l l-Scalar l-Scalar-Plain',
    'bp',
    'c1',
    'ch',
    'c',
    'cp',
    's',
    'sx',
    'fm',
    'k',
    'kc',
    'kn',
    'kt',
    'kd',
    'm',
    'mf',
    'mi',
    'mh',
    'n',
    'ni',
    'nb',
    'nc',
    'nd',
    'ne',
    'nf',
    'nn',
    'na',
    'nv',
    'nt',
    'nl',
    'o',
    'ow',
    'p',
    's1',
    's2',
    'sa',
    'sd',
    'se',
    'si',
    'sb',
    'vm',
    'w',
    'err',
    'gs',
    'gu',
    'nx',
    'gh',
    'ge',
    'math-inline',
    'math-display',
    'math-fraction',
    'math-fraction-numerator',
    'math-fraction-denominator',
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check for new classes in a html file')
    parser.add_argument('html', type=str, help='Path to the notebook')
    args = parser.parse_args()

    check_for_new_classes(args.html)