from tqdm import tqdm
from gemini import Gemini
from gpt4o import GPT4o
from groq_llm import Groq_llama3_1_70B
from notebook import Notebook
import re

ENGLISH = 'en'
PORTUGUESE = 'pt'
TARGET_LANGUAGES = [ENGLISH, PORTUGUESE]
SYSTEM_INSTRUCTION_EN = """
    Eres un experto traductor al inglés de texto markdown. Tu misión es traducir al inglés texto markdown.

    Enfoque en la corrección: Por favor, traduce el texto al inglés, sin modificar la estructura ni el estilo del texto markdown.

    Te van a pasar textos markdown y tienes que traducirlos al español. Responde solo con la traducción, no respondas nada más, solamente la traducción.
"""
SYSTEM_INSTRUCTION_PT = """
    Eres un experto traductor al portugés de texto markdown. Tu misión es traducir al portugés texto markdown.

    Enfoque en la corrección: Por favor, traduce el texto al portugés, sin modificar la estructura ni el estilo del texto markdown.

    Te van a pasar textos markdown y tienes que traducirlos al español. Responde solo con la traducción, no respondas nada más, solamente la traducción.
"""
SYSTEM_INSTRUCTION_CHECKER = """
    Eres un experto en revisión de traducciones. Tu misión es revisar las traducciones de texto en jupyter notebooks.
    Te pasarán dos jupyter notebooks, uno en español y otro traducido a otro idioma que se te especificará en el prompt, y tienes que revisar si las traducciones son correctas.
    Solo estarán traducidas las celdas de tipo markdown, las celdas de tipo código no van a estar traducidas.
    Si crees que la traducción es correcta, responde con "Todo correcto".
    Si crees que hay algún error, responde con "Error" y a continuación el error.
    Si el tipo de celda es de tipo `code`, es decir si tiene `'cell_type': 'code'`, no hace falta que lo revises.
    Recuerda, responde solo lo que te pido, tu respuesta forma parte de un script de automatización que va a comprobar si tu salida es una de las esperadas.
"""
DISCLAIMER_EN = " > Disclaimer: This post has been translated to English using a machine translation model. Please, let me know if you find any mistakes."
DISCLAIMER_PT = " > Aviso: Este post foi traduzido para o português usando um modelo de tradução automática. Por favor, me avise se encontrar algum erro."
GEMINI_LLM = "Gemini"
GPT4o_LLM = "GPT4o"
GROQ_LLM = "Groq_llama3_1_70B"
TRANSLATOR_MODEL = GPT4o_LLM
CHECKER_MODEL = GEMINI_LLM

def translate_text(model, line):
    global translation_counter
    global translation_limit

    # if line has not text, return it. Check with regex if line has only spaces
    if re.match(r"^\s*$", line):
        return line
    correction_string = model.chat(line)
    # correction_string = "```json\n{"
    # corr = "corr "
    # correction_string = correction_string + f"\n    \"{KEY_ORIGINAL}\": \"{line}\",\n    \"{KEY_CORRECTION}\": \"{corr+line}\",\n    \"{KEY_EXPLANATION}\": \"test\"\n"
    # correction_string = correction_string + "}\n```"

    # if correction_string is not string, it's an error
    if type(correction_string) != str:
        print(f"LLM Error ({translation_counter}): {correction_string}")
        exit(1)

    return correction_string

def translate_jupyter_notebook(notebook_path):
    # load translator LLM
    if TRANSLATOR_MODEL == GEMINI_LLM:
        translator_model_en = Gemini(system_instruction=SYSTEM_INSTRUCTION_EN)
        translator_model_pt = Gemini(system_instruction=SYSTEM_INSTRUCTION_PT)
    elif TRANSLATOR_MODEL == GPT4o_LLM:
        translator_model_en = GPT4o(system_instruction=SYSTEM_INSTRUCTION_EN)
        translator_model_pt = GPT4o(system_instruction=SYSTEM_INSTRUCTION_PT)
    elif TRANSLATOR_MODEL == GROQ_LLM:
        translator_model_en = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_EN)
        translator_model_pt = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_PT)
    translations_models = [translator_model_en, translator_model_pt]

    # load checker LLM
    if CHECKER_MODEL == GEMINI_LLM:
        checker_model = Gemini(system_instruction=SYSTEM_INSTRUCTION_CHECKER)
    elif CHECKER_MODEL == GPT4o_LLM:
        checker_model = GPT4o(system_instruction=SYSTEM_INSTRUCTION_CHECKER)
    elif CHECKER_MODEL == GROQ_LLM:
        checker_model = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_CHECKER)

    # Get notebook content as a dictionary
    notebook = Notebook(notebook_path)
    notebook_content_dict = notebook.get_content_as_json()
    cells = notebook.cells()   # Get only with the cells
    total_markdown_cells = notebook.number_markdown_cells()

    # Create a new notebook for each target language
    notebook_en = Notebook(notebook_path, add_path='notebooks_translated', end_name=ENGLISH)
    notebook_pt = Notebook(notebook_path, add_path='notebooks_translated', end_name=PORTUGUESE)
    notebook_en.copy_from(notebook)
    notebook_pt.copy_from(notebook)
    cells_en = notebook_en.cells()
    cells_pt = notebook_pt.cells()
    target_notebooks = [notebook_en, notebook_pt]
    target_cells = [cells_en, cells_pt]

    # Iterate for each cell in the notebook
    print(f"\tTranslating {notebook_path}")
    bar = tqdm(cells, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    markdown_cell_counter = 0
    for cell_counter, cell in enumerate(bar):
        # if cell_counter == 8:
        #     break
        if cell['cell_type'] == 'markdown':
            for notebook_number, notebook in enumerate(target_notebooks):
                if type(cell['source']) == str:
                    target_cells[notebook_number][cell_counter]['source'] = translate_text(translations_models[notebook_number], cell['source'])
                elif type(cell['source']) == list:
                    for number_line, line in enumerate(cell['source']):
                        target_cells[notebook_number][cell_counter]['source'][number_line] = translate_text(translations_models[notebook_number], line)
            markdown_cell_counter += 1
        bar.set_description(f"\t\tCell {markdown_cell_counter}/{total_markdown_cells}")
    print(f"\tEnd of translation")

    # Check translations
    for notebook_number, notebook in enumerate(target_notebooks):
        prompt = """
            Hola, tengo este jupyter notebook en español
            ```
            """ + str(notebook.content['cells']) + """
            ```
            y lo he traducido al """ + TARGET_LANGUAGES[notebook_number] + """
            ```
            """ + str(target_notebooks[notebook_number].content['cells']) + """
            ```
            ¿Podrías revisarlo y decirme si hay algún error? 
            Si crees que está todo bien respondeme con "Todo correcto".
            Si crees que hay algún error respondeme con "Error" y a continuación el error.
            Recuerda, responde solo lo que te pido, tu respuesta forma parte de un script de automatización que va a comprobar si tu salida es una de las esperadas.
        """
        translation_check = checker_model.chat(prompt)
        if translation_check == "Error":
            print(f"Error in {TARGET_LANGUAGES[notebook_number]} translation")
            print(f"Error: {translation_check}")
            exit(1)
        elif translation_check != "Todo correcto":
            print(f"Error in {TARGET_LANGUAGES[notebook_number]} translation")
            print(f"Error: {translation_check}")
            exit(1)

    # Append at position 1 the disclaimer
    cells_en.insert(1, cells_en[0].copy())
    cells_pt.insert(1, cells_pt[0].copy())
    cells_en[1]['source'] = [DISCLAIMER_EN]
    cells_pt[1]['source'] = [DISCLAIMER_PT]

    # Save translated notebooks
    for notebook_number, notebook in enumerate(target_notebooks):
        notebook.save_cells(target_cells[notebook_number])