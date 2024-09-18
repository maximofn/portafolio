import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import argparse
from error_codes import QUOTA_EXCEEDED_ERROR
from get_notebook_metadata import get_portafolio_path
from sentence_transformers import SentenceTransformer
import torch
from torch.nn.functional import cosine_similarity
from utils import ask_for_something

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
        system_instruction="Eres un experto corrector de jupyter notebooks. Tu misión es corregir ortograficamente jupyter notebooks.\n\nEnfoque en la corrección: Por favor, revisa el siguiente texto y corrige únicamente los errores ortográficos, sin modificar la estructura, el estilo ni el contenido. No hagas cambios del tipo 'Con estos modelos podemos hacer...' a 'Con estos modelos se puede hacer...', tampoco quiero cambios del tipo 'Podemos obtener la longitud de nuestro string mediante la función `len()`' a 'Podemos obtener la longitud de nuestro string mediante la función `len()`.' es decir, no añadas puntos al final de la oración, solo corrige si hay errores de ortografía.\n\nTe van a pasar jupyter notebooks y tienes que corregirlos ortograficamente en español. Ten en cuenta que las celdas de código no hay que corregirlas. Responde solo con las celdas que tienen errores ortograficos, responde con el texto que hay y la corrección que sugieres.\n\nEl formato de salida tiene que ser un json con llaves llamadas `correccionX` donde `X` será un número que comenzará desde 0 e irá incrementando. Dentro de cada corrección habrá otras tres llaves, una será `original`, otra `correccion` y la última será `explicación` con la explicación de qué cambia y por qué\n\nRecuerda, rellena el json solo con las celdas que tienen errores, no pongas en el json las que no tienen errores y no quiero que añadir un punto al final de la oración sea una corrección",
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
        else:
            response = None
    return response.text

def get_notebook_content(notebook_path):
    with open(notebook_path, 'r') as file:
        return file.read()

def notebook_string_content_to_dict(notebook_content):
    filter_text = notebook_content.replace('```json', '').replace('\n', '').replace('```', '')
    notebook_content_json = json.loads(filter_text)
    notebook_content_dict = dict(notebook_content_json)

def clean_gemini_correctios(correctios):
    filter_text = correctios.replace('```json', '').replace('```', '').replace(',"', ',\\"').replace(',\\"\\n"', ',\\"\\n\\"').replace('\\n",', '\\n\\",')
    
    # iterate for each line in the text
    filter_text = filter_text.split('\n')
    for i in range(len(filter_text)):
        if filter_text[i].endswith('\\n\\",'):
            # Replace \n\", with \n", at the end of the line
            filter_text[i] = filter_text[i].replace('\\n\\",', '\\n",')
    filter_text = '\n'.join(filter_text)

    return filter_text

def string_to_dict(string):
    notebook_content_json = json.loads(string)
    notebook_content_dict = dict(notebook_content_json)
    return notebook_content_dict

def get_path_name_and_extension(path):
    # return path, name and extension of a file
    path_name, extension = os.path.splitext(path)
    file_name = path_name.split('/')[-1]
    path = path_name.replace(file_name, '')
    return path, file_name, extension

def save_corrections_dict(file_name, corrections_dict):
    portfolio_path = get_portafolio_path(os.getcwd())

    json_path = os.path.join(portfolio_path, 'preparar_notebook/corrections', f'{file_name}.json')

    with open(json_path, 'w') as file:
        json.dump(corrections_dict, file)

def save_corrections_raw(file_name, corrections_raw):
    portfolio_path = get_portafolio_path(os.getcwd())

    json_path = os.path.join(portfolio_path, 'preparar_notebook/corrections', f'{file_name}_raw.json')

    # Write the corrections in a json file, creating it if it doesn't exist
    with open(json_path, 'w') as file:
        file.write(corrections_raw)

def save_corrections_cleaned(file_name, corrections_raw):
    portfolio_path = get_portafolio_path(os.getcwd())

    json_path = os.path.join(portfolio_path, 'preparar_notebook/corrections', f'{file_name}_cleaned.json')

    # Write the corrections in a json file, creating it if it doesn't exist
    with open(json_path, 'w') as file:
        file.write(corrections_raw)

def create_corrections_dict(notebook_path):
    load_gemini_api_key()
    model = create_model()
    _, notebook_name, _ = get_path_name_and_extension(notebook_path)

    notebook_content = get_notebook_content(notebook_path)

    gemini_corrections = chat_with_gemini(model, notebook_content)
    # with open("/home/wallabot/Documentos/web/portafolio/preparar_notebook/corrections/2021-02-11-Introduccion-a-Python_copy.json", 'r') as file:
    #     gemini_corrections = file.read()
    if not gemini_corrections:
        return None
    elif gemini_corrections == QUOTA_EXCEEDED_ERROR:
        return QUOTA_EXCEEDED_ERROR
    save_corrections_raw(notebook_name, gemini_corrections)
    gemini_corrections_cleaned = clean_gemini_correctios(gemini_corrections)
    save_corrections_cleaned(notebook_name, gemini_corrections_cleaned)
    gemini_correctios_dict = string_to_dict(gemini_corrections_cleaned)

    # gemini_correctios_dict = {
    #     "correccion0": {
    #         "original": "Para escribir un `string` muy largo y no tener una fila que ocupe mucho espacio se puede introducir en varias lineas",
    #         "correccion": "Para escribir un `string` muy largo y no tener una fila que ocupe mucho espacio se puede introducir en varias líneas",
    #         "explicación": "Se ha corregido \"lineas\" por \"líneas\"."
    #     },
    #     "correccion1": {
    #         "original": "Sin embargo vemos que en medio ha metido el caracter `\\n`, este caracter indica el salto de linea. Si usamos la función `print()` veremos como ya no aparece",
    #         "correccion": "Sin embargo vemos que en medio ha metido el carácter `\\n`, este carácter indica el salto de línea. Si usamos la función `print()` veremos como ya no    aparece",
    #         "explicación": "Se ha corregido \"caracter\" por \"carácter\" (dos veces) y \"linea\" por \"línea\"."
    #     },
    #     "correccion2": {
    #         "original": "Como hemos dicho los strings son cadenas de caracteres, por lo que podemos navegar e iterar a traves de ellos",
    #         "correccion": "Como hemos dicho los strings son cadenas de caracteres, por lo que podemos navegar e iterar a través de ellos",
    #         "explicación": "Se ha corregido \"a traves\" por \"a través\"."
    #     },
    #     "correccion3": {
    #         "original": "Antes explicamos que el caracter `\\n` correspondía a una salto de linea, este caracter especial corresponde a una serie de caracteres especiales llamados     `Escape Characters`. Veamos otros",
    #         "correccion": "Antes explicamos que el carácter `\\n` correspondía a un salto de línea, este carácter especial corresponde a una serie de caracteres especiales llamados    `Escape Characters`. Veamos otros",
    #         "explicación": "Se ha corregido \"caracter\" por \"carácter\" (dos veces), \"una salto\" por \"un salto\" y \"linea\" por \"línea\"."
    #     },
    # }
    save_corrections_dict(notebook_name, gemini_correctios_dict)

    return 0

def codification_characters_to_ansi(text):
    # ANSI UTF-8	JAVASCRIPT	HTML
    # Â	   u00a0	&#160;
    # ¡	   Â¡	u00a1	&#161;
    # ¢	   Â¢	u00a2	&#162;
    # £	   Â£	u00a3	&#163;
    # ¤	   Â¤	u00a4	&#164;
    # ¥	   Â¥	u00a5	&#165;
    # ¦	   Â¦	u00a6	&#166;
    # §	   Â§	u00a7	&#167;
    # ¨	   Â¨	u00a8	&#168;
    # ©	   Â©	u00a9	&#169;
    # ª	   Âª	u00aa	&#170;
    # «	   Â«	u00ab	&#171;
    # ¬	   Â¬	u00ac	&#172;
    # ­	    Â­	  u00ad	&#173;
    # ®	   Â®	u00ae	&#174;
    # ¯	   Â¯	u00af	&#175;
    # °	   Â°	u00b0	&#176;
    # ±	   Â±	u00b1	&#177;
    # ²	   Â²	u00b2	&#178;
    # ³	   Â³	u00b3	&#179;
    # ´	   Â´	u00b4	&#180;
    # µ	   Âµ	u00b5	&#181;
    # ¶	   Â¶	u00b6	&#182;
    # ·	   Â·	u00b7	&#183;
    # ¸	   Â¸	u00b8	&#184;
    # ¹	   Â¹	u00b9	&#185;
    # º	   Âº	u00ba	&#186;
    # »	   Â»	u00bb	&#187;
    # ¼	   Â¼	u00bc	&#188;
    # ½	   Â½	u00bd	&#189;
    # ¾	   Â¾	u00be	&#190;
    # ¿	   Â¿	u00bf	&#191;
    # À	   Ã€	u00c0	&#192;
    # Á	   Ã	u00c1	&#193;
    # Â	   Ã‚	u00c2	&#194;
    # Ã	   Ãƒ	u00c3	&#195;
    # Ä	   Ã„	u00c4	&#196;
    # Å	   Ã…	u00c5	&#197;
    # Æ	   Ã†	u00c6	&#198;
    # Ç	   Ã‡	u00c7	&#199;
    # È	   Ãˆ	u00c8	&#200;
    # É	   Ã‰	u00c9	&#201;
    # Ê	   ÃŠ	u00ca	&#202;
    # Ë	   Ã‹	u00cb	&#203;
    # Ì	   ÃŒ	u00cc	&#204;
    # Í	   Ã	u00cd	&#205;
    # Î	   ÃŽ	u00ce	&#206;
    # Ï	   Ã	u00cf	&#207;
    # Ð	   Ã	u00d0	&#208;
    # Ñ	   Ã‘	u00d1	&#209;
    # Ò	   Ã’	u00d2	&#210;
    # Ó	   Ã“	u00d3	&#211;
    # Ô	   Ã”	u00d4	&#212;
    # Õ	   Ã•	u00d5	&#213;
    # Ö	   Ã–	u00d6	&#214;
    # ×	   Ã—	u00d7	&#215;
    # Ø	   Ã˜	u00d8	&#216;
    # Ù	   Ã™	u00d9	&#217;
    # Ú	   Ãš	u00da	&#218;
    # Û	   Ã›	u00db	&#219;
    # Ü	   Ãœ	u00dc	&#220;
    # Ý	   Ã	u00dd	&#221;
    # Þ	   Ãž	u00de	&#222;
    # ß	   ÃŸ	u00df	&#223;
    # à	   Ã	u00e0	&#224;
    # á	   Ã¡	u00e1	&#225;
    # â	   Ã¢	u00e2	&#226;
    # ã	   Ã£	u00e3	&#227;
    # ä	   Ã¤	u00e4	&#228;
    # å	   Ã¥	u00e5	&#229;
    # æ	   Ã¦	u00e6	&#230;
    # ç	   Ã§	u00e7	&#231;
    # è	   Ã¨	u00e8	&#232;
    # é	   Ã©	u00e9	&#233;
    # ê	   Ãª	u00ea	&#234;
    # ë	   Ã«	u00eb	&#235;
    # ì	   Ã¬	u00ec	&#236;
    # í	   Ã­	u00ed	&#237;
    # î	   Ã®	u00ee	&#238;
    # ï	   Ã¯	u00ef	&#239;
    # ð	   Ã°	u00f0	&#240;
    # ñ	   Ã±	u00f1	&#241;
    # ò	   Ã²	u00f2	&#242;
    # ó	   Ã³	u00f3	&#243;
    # ô	   Ã´	u00f4	&#244;
    # õ	   Ãµ	u00f5	&#245;
    # ö	   Ã¶	u00f6	&#246;
    # ÷	   Ã·	u00f7	&#247;
    # ø	   Ã¸	u00f8	&#248;
    # ù	   Ã¹	u00f9	&#249;
    # ú	   Ãº	u00fa	&#250;
    # û	   Ã»	u00fb	&#251;
    # ü	   Ã¼	u00fc	&#252;
    # ý	   Ã½	u00fd	&#253;
    # þ	   Ã¾	u00fe	&#254;
    # ÿ	   Ã¿	u00ff	&#255;
    return text.replace('\u00a0', '').replace('\u00a1', '¡').replace('\u00a2', '¢').replace('\u00a3', '£').replace('\u00a4', '¤').replace('\u00a5', '¥').replace('\u00a6', '¦').replace('\u00a7', '§').replace('\u00a8', '¨').replace('\u00a9', '©').replace('\u00aa', 'ª').replace('\u00ab', '«').replace('\u00ac', '¬').replace('\u00ad', '­').replace('\u00ae', '®').replace('\u00af', '¯').replace('\u00b0', '°').replace('\u00b1', '±').replace('\u00b2', '²').replace('\u00b3', '³').replace('\u00b4', '´').replace('\u00b5', 'µ').replace('\u00b6', '¶').replace('\u00b7', '·').replace('\u00b8', '¸').replace('\u00b9', '¹').replace('\u00ba', 'º').replace('\u00bb', '»').replace('\u00bc', '¼').replace('\u00bd', '½').replace('\u00be', '¾').replace('\u00bf', '¿').replace('\u00c0', 'À').replace('\u00c1', 'Á').replace('\u00c2', 'Â').replace('\u00c3', 'Ã').replace('\u00c4', 'Ä').replace('\u00c5', 'Å').replace('\u00c6', 'Æ').replace('\u00c7', 'Ç').replace('\u00c8', 'È').replace('\u00c9', 'É').replace('\u00ca', 'Ê').replace('\u00cb', 'Ë').replace('\u00cc', 'Ì').replace('\u00cd', 'Í').replace('\u00ce', 'Î').replace('\u00cf', 'Ï').replace('\u00d0', 'Ð').replace('\u00d1', 'Ñ').replace('\u00d2', 'Ò').replace('\u00d3', 'Ó').replace('\u00d4', 'Ô').replace('\u00d5', 'Õ').replace('\u00d6', 'Ö').replace('\u00d7', '×').replace('\u00d8', 'Ø').replace('\u00d9', 'Ù').replace('\u00da', 'Ú').replace('\u00db', 'Û').replace('\u00dc', 'Ü').replace('\u00dd', 'Ý').replace('\u00de', 'Þ').replace('\u00df', 'ß').replace('\u00e0', 'à').replace('\u00e1', 'á').replace('\u00e2', 'â').replace('\u00e3', 'ã').replace('\u00e4', 'ä').replace('\u00e5', 'å').replace('\u00e6', 'æ').replace('\u00e7', 'ç').replace('\u00e8', 'è').replace('\u00e9', 'é').replace('\u00ea', 'ê').replace('\u00eb', 'ë').replace('\u00ec', 'ì').replace('\u00ed', 'í').replace('\u00ee', 'î').replace('\u00ef', 'ï').replace('\u00f0', 'ð').replace('\u00f1', 'ñ').replace('\u00f2', 'ò').replace('\u00f3', 'ó').replace('\u00f4', 'ô').replace('\u00f5', 'õ').replace('\u00f6', 'ö').replace('\u00f7', '÷').replace('\u00f8', 'ø').replace('\u00f9', 'ù').replace('\u00fa', 'ú').replace('\u00fb', 'û').replace('\u00fc', 'ü').replace('\u00fd', 'ý').replace('\u00fe', 'þ').replace('\u00ff', 'ÿ')

def load_encoder_model():
    global ENCODER_MODEL
    print("Loading encoder model...")
    ENCODER_MODEL = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    ENCODER_MODEL.eval()
    print("Encoder model loaded")

def get_similarity_between_strings(string1, string2):
    embedding1 = torch.from_numpy(ENCODER_MODEL.encode(string1))
    embedding2 = torch.from_numpy(ENCODER_MODEL.encode(string2))

    similarity = cosine_similarity(embedding1.unsqueeze(0), embedding2.unsqueeze(0))
    return similarity.item()

def apply_corrections(notebook_path, corrections_dict):
    # Get notebook content and convert it to a dictionary
    with open(notebook_path, 'r') as file:
        notebook_content = file.read()
    notebook_content_dict = json.loads(notebook_content)

    # Init encoder model
    load_encoder_model()
    
    # Apply corrections
    total_number_corrections = len(corrections_dict)
    for i, correction in enumerate(corrections_dict):
        original_text = corrections_dict[correction]['original']
        corrected_text = corrections_dict[correction]['correccion']
        explain_text = corrections_dict[correction]['explicación']

        original_text_founded = False
        for cell in notebook_content_dict['cells']: # Iterate over cells
            for j in range(len(cell['source'])):    # Iterate over cell sources, all the text in a cell
                similarity = get_similarity_between_strings(original_text, cell['source'][j])
                if similarity > SIMILARITY_THRESHOLD:
                    original_text_founded = True
                    print(f"\nCorrection {i} of {total_number_corrections}: {explain_text}")
                    # print(f"\tOriginal : {original_text}")
                    print(f"\tOriginal : {cell['source'][j]}")
                    print(f"\tCorrected: {corrected_text}")
                    if ask_for_something("Do you want to apply this correction? (y/n)", ['y', 'yes'], ['n', 'no']):
                        cell['source'][j] = cell['source'][j].replace(original_text, corrected_text)
                        print("Correction applied")
                    else:
                        print("Correction not applied")
                    break   # Break the loop over cell sources, all the text in a cell
            if original_text_founded:
                break   # Break the loop over cells
        
        # If the original text is not found, print the correction and ask the user to apply it manually
        if not original_text_founded:
            print(f"\nCorrection {i} not found: {explain_text}")
            print(f"\tOriginal : {original_text}")
            print(f"\tCorrected: {corrected_text}")
            if ask_for_something("Change it manually. Done? type 'done' or 'd' to continue", ['d', 'done'], ['']):
                print("Correction applied manually")

    # Save the corrected notebook
    with open(notebook_path, 'w') as file:
        json.dump(notebook_content_dict, file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess a Jupyter notebook')
    parser.add_argument('notebook_path', type=str, help='Path to the notebook')
    args = parser.parse_args()
    notebook_path = args.notebook_path

    gemini_correctios_dict = create_corrections_dict(notebook_path)
    print(gemini_correctios_dict)