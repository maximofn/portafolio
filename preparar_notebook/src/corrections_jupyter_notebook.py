from utils import ask_for_something, string_to_dict
from tqdm import tqdm
import os
import git
from gemini import Gemini
from gpt4o import GPT4o
from groq_llm import Groq_llama3_1_70B
from qwen2_5_72B import Qwen2_5_72B
from ollama_qwen_2_5_7B import Ollama_qwen2_5_7B
from ollama_qwen_2_5_72B import Ollama_qwen2_5_72B
from mlx_qwen_3_0_6B import MLX_Qwen3_0_6B
from mlx_qwen_3_4B import MLX_Qwen3_4B
from mlx_qwen_3_14B import MLX_Qwen3_14B
from notebook_utils import Notebook

KEY_ORIGINAL = "original"
KEY_CORRECTION = "correccion"
KEY_EXPLANATION = "explicación"
SYSTEM_INSTRUCTION = """Eres un experto corrector de texto que SÓLO responde con JSON.
Tu misión es corregir ortográficamente texto.

Instrucciones:
1. Revisa el texto que te proporciono.
2. Corrige ÚNICAMENTE errores ortográficos en español. No cambies el contenido, estilo, ni palabras en inglés.
3. Tu respuesta DEBE SER un objeto JSON y NADA MÁS.
4. El JSON debe tener tres claves: "original", "correccion", y "explicación".
5. Si no hay errores, devuelve un JSON con todas las claves y sus valores como strings vacíos.

Ejemplo de JSON de salida si hay un error:
{
    "original": "El coche es rogo.",
    "correccion": "El coche es rojo.",
    "explicación": "Se corrigió 'rogo' por 'rojo'."
}

Ejemplo de JSON de salida si NO hay errores:
{
    "original": "",
    "correccion": "",
    "explicación": ""
}

NO incluyas "```json" ni "```" en tu respuesta. Responde únicamente con el contenido del JSON.
"""
SYSTEM_CHECK = """
You are a JSON validator. Check if the previous response is a valid JSON with the keys 'original', 'correccion', and 'explicación'.
"""
NUMBER_OF_CHECKS = 0
MAX_TOKENS = 2048
GEMINI_LLM = "Gemini"
GPT4O_LLM = "GPT4o"
GROQ_LLM = "Groq_llama3_1_70B"
QWEN_2_5_72B = "Qwen2.5-72B"
OLLAMA_QWEN_2_5_7B = "Ollama_qwen2_5_7B"
OLLAMA_QWEN_2_5_72B = "Ollama_qwen2_5_72B"
MLX_QWEN_3_0_6B = "MLX_Qwen3_0_6B"
MLX_QWEN_3_4B = "MLX_Qwen3_4B"
MLX_QWEN_3_14B = "MLX_Qwen3_14B"
MODEL = MLX_QWEN_3_4B

def apply_corrections(model, line, debug=False):
    # If line is empty, return it
    if all(char.isspace() for char in line):
        return line
    if line == "\n":
        return line
    if line == "":
        return line
    if line == "\t":
        return line
    if line == "\r":
        return line
    
    # If line is start or end of highlight markdown
    if line.startswith("```"):
        return line

    # If line is only 'o'
    if line.lower() == "o":
        return line

    try:
        correction_string = model.chat(line, debug=debug)
    except Exception as e:
        print(f"Error LLM model chat: {e}")
    # correction_string = "```json\n{"
    # corr = "corr "
    # correction_string = correction_string + f"\n    \"{KEY_ORIGINAL}\": \"{line}\",\n    \"{KEY_CORRECTION}\": \"{corr+line}\",\n    \"{KEY_EXPLANATION}\": \"test\"\n"
    # correction_string = correction_string + "}\n```"

    # if correction_string is not string, it's an error
    if type(correction_string) != str:
        print(f"LLM Error is not a string: {correction_string}")
        return line
    
    # If correction_string has thinking, remove it
    if correction_string.startswith("<think>") and '</think>' in correction_string:
        # Get position of </think>
        position_end_think = correction_string.find('</think>')
        # Get the text between <think> and </think>
        thinking_text = correction_string[0:position_end_think]
        # Remove the thinking text from the correction_string
        correction_string = correction_string[position_end_think+len('</think>'):]

    correction_dict = string_to_dict(correction_string)
    if f"{KEY_EXPLANATION}" in correction_dict.keys() and f"{KEY_CORRECTION}" in correction_dict.keys() and f"{KEY_ORIGINAL}" in correction_dict.keys():
        if len(correction_dict[f'{KEY_EXPLANATION}']) > 0:
            original_value = correction_dict[f'{KEY_ORIGINAL}']
            correction_vaue = correction_dict[f'{KEY_CORRECTION}']
            explanation_value = correction_dict[f'{KEY_EXPLANATION}']
            # print(f"\n{KEY_ORIGINAL}  : {original_value}\n{KEY_CORRECTION}: {correction_vaue}\n{KEY_EXPLANATION}: {explanation_value}")
            # if ask_for_something("Do you want to apply this correction? (y/n)", ['y', 'yes'], ['n', 'no']):
            #     return correction_vaue
            # else:
            #     return original_value
            return correction_vaue
        else:
            return line
    else:
        return line

def is_file_in_git_changes(file_path):
    """
    Comprueba si un archivo está en la lista de cambios de git usando gitpython
    Args:
        file_path: Ruta al archivo a comprobar
    Returns:
        bool: True si el archivo está en la lista de cambios, False en caso contrario
    """
    try:
        # Inicializamos el repositorio
        repo = git.Repo(search_parent_directories=True)
        
        # Obtenemos el path relativo al repositorio
        relative_path = os.path.relpath(file_path, repo.working_dir)
        
        # Comprobamos si el archivo está en el índice o sin seguimiento
        diff_index = repo.index.diff(None)  # Cambios sin staging
        diff_staged = repo.index.diff('HEAD')  # Cambios en staging
        untracked = repo.untracked_files  # Archivos sin seguimiento
        
        # Verificamos si el archivo está en alguna de las listas de cambios
        return any([
            any(d.a_path == relative_path or d.b_path == relative_path for d in diff_index),
            any(d.a_path == relative_path or d.b_path == relative_path for d in diff_staged),
            relative_path in untracked
        ])
        
    except git.exc.InvalidGitRepositoryError:
        print("No se encontró un repositorio git válido")
        return False
    except Exception as e:
        print(f"Error al comprobar el estado de git para {file_path}: {e}")
        return False

def ortografic_corrections_jupyter_notebook(notebook_path):
    # load LLM
    if MODEL == GEMINI_LLM:
        model = Gemini(system_instruction=SYSTEM_INSTRUCTION)
    elif MODEL == GPT4O_LLM:
        model = GPT4o(system_instruction=SYSTEM_INSTRUCTION)
    elif MODEL == GROQ_LLM:
        model = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION)
    elif MODEL == QWEN_2_5_72B:
        model = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)
    elif MODEL == OLLAMA_QWEN_2_5_7B:
        model = Ollama_qwen2_5_7B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)
    elif MODEL == OLLAMA_QWEN_2_5_72B:
        model = Ollama_qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)
    elif MODEL == MLX_QWEN_3_0_6B:
        model = MLX_Qwen3_0_6B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)
    elif MODEL == MLX_QWEN_3_4B:
        model = MLX_Qwen3_4B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)
    elif MODEL == MLX_QWEN_3_14B:
        model = MLX_Qwen3_14B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)

    # Get notebook name
    notebook_name = os.path.basename(notebook_path)
    print(f"Notebook name: {notebook_name}")
    
    # Comprobar si el notebook tiene cambios en git
    if is_file_in_git_changes(notebook_path):
        print(f"The notebook {notebook_name} has changes in git. First commit it and then run the script again.")
        exit(1)

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
    print(f"\tEnd of corrections")

    # Save the notebook with the corrections
    notebook.save_cells(cells)
