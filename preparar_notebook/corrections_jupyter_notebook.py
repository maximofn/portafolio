from utils import ask_for_something, string_to_dict
from tqdm import tqdm
from gemini import Gemini
from gpt4o import GPT4o
from groq_llm import Groq_llama3_1_70B
from notebook import Notebook

KEY_ORIGINAL = "original"
KEY_CORRECTION = "correccion"
KEY_EXPLANATION = "explicación"
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
GEMINI_LLM = "Gemini"
GPT4O_LLM = "GPT4o"
GROQ_LLM = "Groq_llama3_1_70B"
MODEL = GPT4O_LLM

def apply_corrections(model, line):
    correction_string = model.chat(line)
    # correction_string = "```json\n{"
    # corr = "corr "
    # correction_string = correction_string + f"\n    \"{KEY_ORIGINAL}\": \"{line}\",\n    \"{KEY_CORRECTION}\": \"{corr+line}\",\n    \"{KEY_EXPLANATION}\": \"test\"\n"
    # correction_string = correction_string + "}\n```"

    # if correction_string is not string, it's an error
    if type(correction_string) != str:
        print(f"LLM Error: {correction_string}")
        exit(1)

    correction_dict = string_to_dict(correction_string)
    if f"{KEY_EXPLANATION}" in correction_dict.keys():
        if len(correction_dict[f'{KEY_EXPLANATION}']) > 0:
            original_value = correction_dict[f'{KEY_ORIGINAL}']
            correction_vaue = correction_dict[f'{KEY_CORRECTION}']
            explanation_value = correction_dict[f'{KEY_EXPLANATION}']
            print(f"\n{KEY_ORIGINAL}  : {original_value}\n{KEY_CORRECTION}: {correction_vaue}\n{KEY_EXPLANATION}: {explanation_value}")
            if ask_for_something("Do you want to apply this correction? (y/n)", ['y', 'yes'], ['n', 'no']):
                return correction_vaue
            else:
                return original_value
        else:
            return line

def ortografic_corrections_jupyter_notebook(notebook_path):
    # load LLM
    if MODEL == GEMINI_LLM:
        model = Gemini(system_instruction=SYSTEM_INSTRUCTION)
    elif MODEL == GPT4O_LLM:
        model = GPT4o(system_instruction=SYSTEM_INSTRUCTION)
    elif MODEL == GROQ_LLM:
        model = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION)

    # Get notebook content as a dictionary
    notebook = Notebook(notebook_path)
    notebook_content_dict = notebook.get_content_as_json()
    cells = notebook.cells()   # Get only with the cells
    total_markdown_cells = notebook.number_markdown_cells()

    # Iterate for each cell in the notebook
    print(f"\tCorrections of {notebook_path}")
    bar = tqdm(cells, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    markdown_cell_counter = 0
    for cell_counter, cell in enumerate(bar):
        # if cell_counter == 4:
        #     break
        if cell['cell_type'] == 'markdown':
            if type(cell['source']) == str:
                cell['source'] = apply_corrections(model, cell['source'])
            elif type(cell['source']) == list:
                for number_line, line in enumerate(cell['source']):
                    cell['source'][number_line] = apply_corrections(model, line)
            markdown_cell_counter += 1
        bar.set_description(f"\t\tCell {markdown_cell_counter}/{total_markdown_cells}")
    print(f"\tEnd of translation")

    # Save the notebook with the corrections
    notebook.save_cells(cells)
