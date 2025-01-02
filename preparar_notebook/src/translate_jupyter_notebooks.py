from tqdm import tqdm
from gemini import Gemini
from gpt4o import GPT4o
from groq_llm import Groq_llama3_1_70B
from qwen2_5_72B import Qwen2_5_72B
from ollama_qwen_2_5_7B import Ollama_qwen2_5_7B
from ollama_qwen_2_5_72B import Ollama_qwen2_5_72B
from llama_3_3_70B import Llama_3_3_70B
from notebook_utils import Notebook
import re
from utils import ask_for_something

ENGLISH = 'en'
PORTUGUESE = 'pt'
TARGET_LANGUAJES_DICT = {
    'en': 'english',
    'pt': 'portuguese'
}
TARGET_LANGUAJES = [ENGLISH, PORTUGUESE]
SYSTEM_INSTRUCTION_EN = """
    Eres un experto traductor al inglés de texto markdown. Tu misión es traducir al inglés texto markdown.

    Enfoque en la corrección: Por favor, traduce el texto al inglés, sin modificar la estructura ni el estilo del texto markdown.
    No traduzcas los enlaces ni las imágenes, ni los códigos de programación ni los comandos de terminal.

    Te van a pasar textos markdown y tienes que traducirlos al español. Responde solo con la traducción, no respondas nada más, solamente la traducción.
"""
SYSTEM_INSTRUCTION_PT = """
    Eres un experto traductor al portugés de texto markdown. Tu misión es traducir al portugés texto markdown.

    Enfoque en la corrección: Por favor, traduce el texto al portugés, sin modificar la estructura ni el estilo del texto markdown.
    No traduzcas los enlaces ni las imágenes, ni los códigos de programación ni los comandos de terminal.

    Te van a pasar textos markdown y tienes que traducirlos al español. Responde solo con la traducción, no respondas nada más, solamente la traducción.
"""
SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER = """
    Eres un experto en revisión de traducciones. Tu misión es revisar las traducciones de texto en formato markdown.
    Te pasarán dos frases, una en español y otra traducido a otro idioma que se te especificará en el prompt, y tienes que revisar si las traducciones son correctas.
    Si crees que la traducción es correcta, responde con "Todo correcto".
    Si crees que hay algún error, responde con la traducción correcta.
    Recuerda, responde solo lo que te pido, tu respuesta forma parte de un script de automatización que va a comprobar si tu salida es una de las esperadas.
"""
SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER = """
    Eres un experto en revisión de traducciones. Tu misión es revisar las traducciones de texto en jupyter notebooks.
    Te pasarán dos jupyter notebooks, uno en español y otro traducido a otro idioma que se te especificará en el prompt, y tienes que revisar si las traducciones son correctas.
    Solo estarán traducidas las celdas de tipo markdown, las celdas de tipo código no van a estar traducidas.
    Si crees que la traducción es correcta, responde con "Todo correcto".
    Si crees que hay algún error, responde con "Error" y a continuación el error.
    Si el tipo de celda es de tipo `code`, es decir si tiene `'cell_type': 'code'`, no hace falta que lo revises.
    Recuerda, responde solo lo que te pido, tu respuesta forma parte de un script de automatización que va a comprobar si tu salida es una de las esperadas.
"""
NUMBER_OF_PHRASE_CHECKS = 0
NUMBER_OF_NOTEBOOK_CHECKS = 0
DISCLAIMER_EN = " > Disclaimer: This post has been translated to English using a machine translation model. Please, let me know if you find any mistakes."
DISCLAIMER_PT = " > Aviso: Este post foi traduzido para o português usando um modelo de tradução automática. Por favor, me avise se encontrar algum erro."
GEMINI_LLM = "Gemini"
GPT4o_LLM = "GPT4o"
GROQ_LLM = "Groq_llama3_1_70B"
QWEN_2_5_72B = "Qwen2.5-72B"
LLAMA_3_3_70B = "Llama3.3-70B"
OLLAMA_QWEN_2_5_7B = "Ollama_qwen2_5_7B"
OLLAMA_QWEN_2_5_72B = "Ollama_qwen2_5_72B"
TRANSLATOR_MODEL = QWEN_2_5_72B
CHECKER_MODEL = GEMINI_LLM

def translate_text(model, line, notebook_number):
    # if line has not text, return it. Check with regex if line has only spaces
    if re.match(r"^\s*$", line):
        return line

    # If line is start or end of highlight markdown
    if line.startswith("```"):
        return line

    # If line is only 'o'
    if line.lower() == "o":
        if notebook_number == 0:
            return "or"
        else:
            return "o"
    
    # Translate line with the model
    correction_string = model.chat(line)

    # if correction_string is not string, it's an error
    if type(correction_string) != str:
        print(f"LLM Error: {correction_string}")
        # exit(1)
        print(f"\tline to translate: {line}")

    return correction_string

def analyze_translation_errors(error):
    print(error)
    # Get json
    if "```json" in error:
        error_json_raw = re.search(r"```json(.*)```", error, re.DOTALL).group(1)
    else:
        error_json_raw = re.search(r"```(.*)```", error, re.DOTALL).group(1)
    
    # Clean format if LLM checkers return it with a wrong format
    if error_json_raw.startswith("Error") and not error_json_raw.startswith("Error\n"):
        error_json_raw = error_json_raw[5:]
    elif error_json_raw.startswith("Error\n"):
        error_json_raw = error_json_raw[6:]
    elif error_json_raw.startswith("\nError") and not error_json_raw.startswith("\nError\n"):
        error_json_raw = error_json_raw[6:]
    elif error_json_raw.startswith("\nError\n"):
        error_json_raw = error_json_raw[7:]
    else:
        error_json_raw = error_json_raw
    
    # Clean json
    error_json_raw_cleaned = error_json_raw.replace("'", "\"").replace("{\"", "{\n\"").replace("\"original\"", "\t\"original\"").replace("\"traduccion\"", "\n\t\"traduccion\"").replace("\"error\"", "\n\t\"error\"").replace(", \"", ", \n\"").replace("\"},", "\"\n\t},").replace("\"}}", "\"\n\t}\n}").replace("\n\n", "").replace("[\"", "\"").replace("\"]", "\"")

    # Split json in lines beacuse if I try to convert it to a dictionary, it gives me an error because LLM checker return wrong json
    lines = error_json_raw_cleaned.split("\n")

    # Get cells IDs, original, translation and error and create a dictionary with them
    translation_errors_dict = {}
    for number_line, line in enumerate(lines):
        if line.startswith("\"") and line.endswith("{"):
            key = re.search(r"\"(.*?)\"", line, re.DOTALL).group(1)
            original = lines[number_line + 1]
            translation = lines[number_line + 2]
            error_explained = lines[number_line + 3]
            
            if original.startswith("\t"):
                original = original[1:]
            if translation.startswith("\t"):
                translation = translation[1:]
            if error_explained.startswith("\t"):
                error_explained = error_explained[1:]
            
            if original.startswith("\"original\": ") and translation.startswith("\"traduccion\": ") and error_explained.startswith("\"error\": "):
                original = original.replace("\"original\": ", "")
                translation = translation.replace("\"traduccion\": ", "")
                error_explained = error_explained.replace("\"error\": ", "")
                translation_errors_dict[key] = {"original": original, "translation": translation, "error": error_explained}
            else:
                continue
                
            print(f"\t\tkey: {key}")
            print(f"\t\t\toriginal:    {original}")
            print(f"\t\t\ttranslation: {translation}")
            print(f"\t\t\terror:       {error_explained}")

def translate_jupyter_notebook(notebook_path):
    # load translator LLM
    print(f"\tLoading translator model {TRANSLATOR_MODEL}")
    if TRANSLATOR_MODEL == GEMINI_LLM:
        translator_model_en = Gemini(system_instruction=SYSTEM_INSTRUCTION_EN)
        translator_model_pt = Gemini(system_instruction=SYSTEM_INSTRUCTION_PT)
    elif TRANSLATOR_MODEL == GPT4o_LLM:
        translator_model_en = GPT4o(system_instruction=SYSTEM_INSTRUCTION_EN)
        translator_model_pt = GPT4o(system_instruction=SYSTEM_INSTRUCTION_PT)
    elif TRANSLATOR_MODEL == GROQ_LLM:
        translator_model_en = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_EN)
        translator_model_pt = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_PT)
    elif TRANSLATOR_MODEL == QWEN_2_5_72B:
        translator_model_en = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_EN, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
        translator_model_pt = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_PT, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
    elif TRANSLATOR_MODEL == LLAMA_3_3_70B:
        translator_model_en = Llama_3_3_70B(system_instruction=SYSTEM_INSTRUCTION_EN, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
        translator_model_pt = Llama_3_3_70B(system_instruction=SYSTEM_INSTRUCTION_PT, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
    elif TRANSLATOR_MODEL == OLLAMA_QWEN_2_5_7B:
        translator_model_en = Ollama_qwen2_5_7B(system_instruction=SYSTEM_INSTRUCTION_EN, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
        translator_model_pt = Ollama_qwen2_5_7B(system_instruction=SYSTEM_INSTRUCTION_PT, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
    elif TRANSLATOR_MODEL == OLLAMA_QWEN_2_5_72B:
        translator_model_en = Ollama_qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_EN, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
        translator_model_pt = Ollama_qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_PT, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)
    translations_models = [translator_model_en, translator_model_pt]

    # load checker LLM
    print(f"\tLoading checker model {CHECKER_MODEL}")
    if CHECKER_MODEL == GEMINI_LLM:
        checker_model = Gemini(system_instruction=SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER)
    elif CHECKER_MODEL == GPT4o_LLM:
        checker_model = GPT4o(system_instruction=SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER)
    elif CHECKER_MODEL == GROQ_LLM:
        checker_model = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER)
    elif CHECKER_MODEL == QWEN_2_5_72B:
        checker_model = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER, system_check=SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER, num_checks=NUMBER_OF_NOTEBOOK_CHECKS)

    # Get notebook content as a dictionary
    print(f"\tLoading notebook {notebook_path}")
    notebook = Notebook(notebook_path)
    cells = notebook.cells()   # Get only with the cells
    total_markdown_cells = notebook.number_markdown_cells()

    # Create a new notebook for each target language
    print(f"\tCreating target notebooks")
    notebook_en = Notebook(notebook_path, add_path='notebooks_translated', end_name=ENGLISH.upper())
    notebook_pt = Notebook(notebook_path, add_path='notebooks_translated', end_name=PORTUGUESE.upper())
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
                    target_cells[notebook_number][cell_counter]['source'] = translate_text(translations_models[notebook_number], cell['source'], notebook_number)
                elif type(cell['source']) == list:
                    for number_line, line in enumerate(cell['source']):
                        target_cells[notebook_number][cell_counter]['source'][number_line] = translate_text(translations_models[notebook_number], line, notebook_number)
            markdown_cell_counter += 1
        bar.set_description(f"\t\tCell {markdown_cell_counter}/{total_markdown_cells}")
    print(f"\tEnd of translation")

    # Append at position 1 the disclaimer
    print(f"\tAdding disclaimer to target notebooks")
    cells_en.insert(1, cells_en[0].copy())
    cells_pt.insert(1, cells_pt[0].copy())
    cells_en[1]['source'] = [DISCLAIMER_EN]
    cells_pt[1]['source'] = [DISCLAIMER_PT]
    if 'id' in cells_en[1]['metadata']:
        cells_en[1]['metadata']['id'] += '_discalimer'
        cells_pt[1]['metadata']['id'] += '_discalimer'

    # Save translated notebooks
    print(f"\tSaving target notebooks")
    for notebook_number, notebook in enumerate(target_notebooks):
        notebook.save_cells(target_cells[notebook_number])

    # Check translations
    print(f"\tChecking translations")
    markdown_cells = [cell for cell in cells if cell['cell_type'] == 'markdown']
    cells_en = notebook_en.cells()
    cells_pt = notebook_pt.cells()
    markdown_cells_en = [cell for cell in cells_en if cell['cell_type'] == 'markdown']
    markdown_cells_pt = [cell for cell in cells_pt if cell['cell_type'] == 'markdown']
    target_markdown_cells = [markdown_cells_en, markdown_cells_pt]
    for notebook_number, notebook in enumerate(target_notebooks):
        prompt = f"""
            Hola, tengo este jupyter notebook en español
            ```
            {markdown_cells}
            ```
            y lo he traducido al {TARGET_LANGUAJES_DICT[TARGET_LANGUAJES[notebook_number]]}
            ```
            {target_markdown_cells[notebook_number]}
            ```
            ¿Podrías revisarlo y decirme si hay algún error? 
            Si crees que está todo bien respondeme con "Todo correcto".
            Si crees que hay algún error respondeme con "Error" y a continuación el error que lo mostrarás mediante un json con una clave con cada ID de celda que tiene error.
            Dentro de esa clave habrá otros tres conjuntos de clave valor
             * Uno con la clave `original` y el valor con el contenido original de la celda
             * Otro con la clave `traduccion` y el valor con la traducción de la celda
             * Otro con la clave `error` y el valor con el error que has encontrado
            
            Recuerda, responde solo lo que te pido, tu respuesta forma parte de un script de automatización que va a comprobar si tu salida es una de las esperadas.
        """
        translation_check = checker_model.chat(prompt)
        if translation_check != "Todo correcto":
            print(f"\tError in {TARGET_LANGUAJES_DICT[TARGET_LANGUAJES[notebook_number]].upper()} translation")
            print(translation_check)
            # analyze_translation_errors(translation_check)
            ask_for_something("\nHave you changed this mistakes? (y/n)", ['y', 'yes'], ['n', 'no'])
            # exit(1)

    # Save translated notebooks
    print(f"\tSaving target notebooks")
    for notebook_number, notebook in enumerate(target_notebooks):
        notebook.save_cells(target_cells[notebook_number])

    print(f"\tEnd of translation check")