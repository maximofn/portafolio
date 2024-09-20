import json
from utils import ask_for_something, string_to_dict
from tqdm import tqdm
from gemini import Gemini
from notebook import Notebook

SYSTEM_INSTRUCTION = """
    Eres un experto corrector de texto markdown. Tu misión es corregir ortograficamente texto markdown.

    Enfoque en la corrección: Por favor, revisa el siguiente texto y corrige únicamente los errores ortográficos, sin modificar la estructura, el estilo ni el contenido.
    No hagas cambios del tipo 'Con estos modelos podemos hacer...' a 'Con estos modelos se puede hacer...', tampoco quiero cambios del tipo 'Podemos obtener la longitud de nuestro string mediante la función `len()`' a 'Podemos obtener la longitud de nuestro string mediante la función `len()`.' es decir, no añadas puntos al final de la oración, solo corrige si hay errores de ortografía.

    Te van a pasar textos markdown y tienes que corregirlos ortograficamente en español. Responde solo con la corrección, responde con el texto que hay y la corrección que sugieres.

    El formato de salida tiene que ser un json con llaves llamadas `original`, otra `correccion` y la última será `explicación` con la explicación de qué cambia y por qué. Si no hay errores ortográficos responde ese json con las llaves vacías. Es decir será un json así:
    ```
    {
        "original": "",
        "correccion": "",
        "explicación": ""
    }
    ```

    Recuerda, rellena el json solo con los textos markdown que tienen errores, no pongas en el json los que no tienen errores y no quiero que añadir un punto al final de la oración sea una corrección
"""

def apply_corrections(model, line):
    correction_string = model.chat_with_gemini(line)
    # correction_string = "```json\n{\n    \"original\": \"\",\n    \"correccion\": \"\",\n    \"explicación\": \"\"\n}\n```"

    # if correction_string is not string, it's an error
    if type(correction_string) != str:
        print(f"LLM Error: {correction_string}")
        exit(1)

    correction_dict = string_to_dict(correction_string)
    if "explicación" in correction_dict.keys():
        if len(correction_dict['explicación']) > 0:
            original = correction_dict['original']
            correccion = correction_dict['correccion']
            explicacion = correction_dict['explicación']
            print(f"\nOriginal  : {original}\nCorrección: {correccion}\nExplicación: {explicacion}")
            if ask_for_something("Do you want to apply this correction? (y/n)", ['y', 'yes'], ['n', 'no']):
                return correccion
            else:
                return original
        else:
            return line

def ortografic_corrections_jupyter_notebook(notebook_path):
    # load gemini model
    model = Gemini(system_instruction=SYSTEM_INSTRUCTION)

    # Get notebook content as a dictionary
    notebook = Notebook(notebook_path)
    notebook_content_dict = notebook.get_content_as_json()
    cells = notebook_content_dict['cells']   # Get only with the cells
    total_cells = len(cells)
    markdown_cells = [cell for cell in cells if cell['cell_type'] == 'markdown']
    total_markdown_cells = len(markdown_cells)

    # Iterate for each cell in the notebook
    print(f"\tCorrections of {notebook_path}")
    bar = tqdm(cells, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    number_markdown_cell = 0
    for number_cell, cell in enumerate(bar):
        # if number_cell == 4:
        #     break
        if cell['cell_type'] == 'markdown':
            if type(cell['source']) == str:
                cell['source'] = apply_corrections(model, cell['source'])
            elif type(cell['source']) == list:
                for number_line, line in enumerate(cell['source']):
                    cell['source'][number_line] = apply_corrections(model, line)
            number_markdown_cell += 1
        bar.set_description(f"\t\tCell {number_markdown_cell}/{total_markdown_cells}")
    print(f"\tEnd of translation")

    # Save the notebook with the corrections
    with open(notebook_path, 'w') as file:
        json.dump(notebook_content_dict, file, indent=2)
