import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import argparse
from error_codes import QUOTA_EXCEEDED_ERROR, INTERNAL_ERROR
from get_notebook_metadata import get_portafolio_path
from sentence_transformers import SentenceTransformer
import torch
from torch.nn.functional import cosine_similarity
from utils import ask_for_something
from tqdm import tqdm
from time import sleep

ENCODER_MODEL = None
SIMILARITY_THRESHOLD = 0.9

def load_gemini_api_key():
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        raise ValueError("GEMINI_API_KEY is not set")
    genai.configure(api_key=GEMINI_API_KEY)

def create_model():
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        # generation_config=generation_config,
        # safety_settings = Adjust safety settings # See https://ai.google.dev/gemini-api/docs/safety-settings
        system_instruction="""
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

        Recuerda, rellena el json solo con los textos markdown que tienen errores, no pongas en el json los que no tienen errores y no quiero que añadir un punto al final de la oración sea una corrección""",
    )

    return model

def chat_with_gemini(model, input_text):
    try:
        response = model.generate_content(input_text)
    except Exception as e:
        print(f'Error: {e}')
        if str(QUOTA_EXCEEDED_ERROR) in str(e):
            print('Quota exceeded')
            response = QUOTA_EXCEEDED_ERROR
        elif str(INTERNAL_ERROR) in str(e):
            print('Internal error')
            response = INTERNAL_ERROR
        else:
            print('Unknown error')
            response = None
        return response
    return response.text

def get_notebook_content(notebook_path):
    with open(notebook_path, 'r') as f:
        return json.load(f)

def notebook_string_content_to_dict(notebook_content):
    filter_text = notebook_content.replace('```json', '').replace('\n', '').replace('```', '')
    notebook_content_json = json.loads(filter_text)
    notebook_content_dict = dict(notebook_content_json)
    return notebook_content_dict

def apply_corrections(model, line):
    correction_string = chat_with_gemini(model, line)
    # correction_string = "```json\n{\n    \"original\": \"\",\n    \"correccion\": \"\",\n    \"explicación\": \"\"\n}\n```"

    # if correction_string is not string, it's an error
    if type(correction_string) != str:
        print(f"Gemini Error: {correction_string}")
        exit(1)
    correction_dict = notebook_string_content_to_dict(correction_string)
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
    load_gemini_api_key()
    model = create_model()

    # Get notebook content as a dictionary
    notebook_content_dict = get_notebook_content(notebook_path)
    cells = notebook_content_dict['cells']   # Get only with the cells
    total_cells = len(cells)
    markdown_cells = [cell for cell in cells if cell['cell_type'] == 'markdown']
    total_markdown_cells = len(markdown_cells)

    # Iterate for each cell in the notebook
    print(f"\tCorrections of {notebook_path}")
    bar = tqdm(cells, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    number_markdown_cell = 0
    for number_cell, cell in enumerate(bar):
        if number_cell == 10:
            break
        if cell['cell_type'] == 'markdown':
            if type(cell['source']) == str:
                # cell['source'] = apply_corrections(model, cell['source'])
                apply_corrections(model, cell['source'])
            elif type(cell['source']) == list:
                for number_line, line in enumerate(cell['source']):
                    # line = apply_corrections(model, line)
                    apply_corrections(model, line)
            number_markdown_cell += 1
            sleep(0.1)
        bar.set_description(f"\t\tCell {number_markdown_cell}/{total_markdown_cells}")
    print(f"\tEnd of translation")