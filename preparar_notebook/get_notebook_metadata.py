import argparse
import json
from PIL import Image
import pathlib
import os

BYPASS_CHECK_METADATA = False

MAXIMO_FN_KEY = 'maximofn'

PORTAFOLIO_FOLDER = 'portafolio'    # portAfolio not portfolio
WEB_PORTFOLIO_PATH = 'portfolio'    # portfolio not portAfolio
WEB_PUBLIC_PATH = 'public'

COUNTER = 0
LIMIT_COUNTER = 10

TITLE_ES_KEY = 'title_es'
TITLE_EN_KEY = 'title_en'
TITLE_PT_KEY = 'title_pt'
END_URL_KEY = 'end_url'
DESCRIPTION_ES_KEY = 'description_es'
DESCRIPTION_EN_KEY = 'description_en'
DESCRIPTION_PT_KEY = 'description_pt'
KEYWORDS_ES_KEY = 'keywords_es'
KEYWORDS_EN_KEY = 'keywords_en'
KEYWORDS_PT_KEY = 'keywords_pt'
IMAGE_KEY = 'image'
DATE_KEY = 'date'

def get_portafolio_path(path):
    global COUNTER
    path = pathlib.Path(path)
    parent = path.parent
    last_folder = path.parts[-1]
    if last_folder == PORTAFOLIO_FOLDER:
        return path
    else:
        if COUNTER < LIMIT_COUNTER:
            COUNTER += 1
            return get_portafolio_path(parent)
        else:
            raise Exception('Portafolio folder not found')

def get_image_width_height(image_path):
    if image_path[0] == '/':
        image_path = image_path[1:]

    # Get current path
    pwd_path = pathlib.Path().absolute()

    # Get portafolio path, this is the main git repository path
    portafolio_path = pathlib.Path(get_portafolio_path(pwd_path))

    # Get image absolute path
    image_absolute_path = portafolio_path / WEB_PORTFOLIO_PATH / WEB_PUBLIC_PATH / image_path

    # Open image and get width and height
    with Image.open(image_absolute_path) as img:
        width, height = img.size
    return width, height

def get_image_extension(image_path):
    return image_path.split('.')[-1]

def get_notebook_metadata(notebook_path):
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    title_es = None
    title_en = None
    title_pt = None
    end_url = None
    description_es = None
    description_en = None
    description_pt = None
    keywords_es = None
    keywords_en = None
    keywords_pt = None
    image = None
    witdh = None
    height = None
    image_extension = None
    date = None

    metadata = notebook.get('metadata', {})

    if MAXIMO_FN_KEY in metadata.keys():
        title_es_in_metadata = TITLE_ES_KEY in metadata[MAXIMO_FN_KEY].keys()
        title_en_in_metadata = TITLE_EN_KEY in metadata[MAXIMO_FN_KEY].keys()
        title_pt_in_metadata = TITLE_PT_KEY in metadata[MAXIMO_FN_KEY].keys()
        end_url_in_metadata = END_URL_KEY in metadata[MAXIMO_FN_KEY].keys()
        description_es_in_metadata = DESCRIPTION_ES_KEY in metadata[MAXIMO_FN_KEY].keys()
        description_en_in_metadata = DESCRIPTION_EN_KEY in metadata[MAXIMO_FN_KEY].keys()
        description_pt_in_metadata = DESCRIPTION_PT_KEY in metadata[MAXIMO_FN_KEY].keys()
        keywords_es_in_metadata = KEYWORDS_ES_KEY in metadata[MAXIMO_FN_KEY].keys()
        keywords_en_in_metadata = KEYWORDS_EN_KEY in metadata[MAXIMO_FN_KEY].keys()
        keywords_pt_in_metadata = KEYWORDS_PT_KEY in metadata[MAXIMO_FN_KEY].keys()
        image_in_metadata = IMAGE_KEY in metadata[MAXIMO_FN_KEY].keys()
        date_in_metadata = DATE_KEY in metadata[MAXIMO_FN_KEY].keys()

        if title_es_in_metadata and title_en_in_metadata and title_pt_in_metadata and end_url_in_metadata and \
            description_es_in_metadata and description_en_in_metadata and description_pt_in_metadata and \
            keywords_es_in_metadata and keywords_en_in_metadata and keywords_pt_in_metadata and \
            image_in_metadata and date_in_metadata:
                title_es = metadata[MAXIMO_FN_KEY][TITLE_ES_KEY]
                title_en = metadata[MAXIMO_FN_KEY][TITLE_EN_KEY]
                title_pt = metadata[MAXIMO_FN_KEY][TITLE_PT_KEY]
                end_url = metadata[MAXIMO_FN_KEY][END_URL_KEY]
                description_es = metadata[MAXIMO_FN_KEY][DESCRIPTION_ES_KEY]
                description_en = metadata[MAXIMO_FN_KEY][DESCRIPTION_EN_KEY]
                description_pt = metadata[MAXIMO_FN_KEY][DESCRIPTION_PT_KEY]
                keywords_es = metadata[MAXIMO_FN_KEY][KEYWORDS_ES_KEY]
                keywords_en = metadata[MAXIMO_FN_KEY][KEYWORDS_EN_KEY]
                keywords_pt = metadata[MAXIMO_FN_KEY][KEYWORDS_PT_KEY]
                image = metadata[MAXIMO_FN_KEY][IMAGE_KEY]
                witdh, height = get_image_width_height(image)
                image_extension = get_image_extension(image)
                date = metadata[MAXIMO_FN_KEY][DATE_KEY]
        
        else:
            print('Some metadata keys are missing')

    else:
        print('No maximofn key in metadata')

    return title_es, title_en, title_pt, end_url, description_es, description_en, description_pt, \
        keywords_es, keywords_en, keywords_pt, image, witdh, height, image_extension, date

def check_if_notebook_metadata_is_ok(metadata):
    print("Metadata of notebook:")
    print(f"\tTitle ES: {metadata[0]}")
    print(f"\tTitle EN: {metadata[1]}")
    print(f"\tTitle PT: {metadata[2]}")
    print(f"\tEnd URL: {metadata[3]}")
    print(f"\tDescription ES: {metadata[4]}")
    print(f"\tDescription EN: {metadata[5]}")
    print(f"\tDescription PT: {metadata[6]}")
    print(f"\tKeywords ES: {metadata[7]}")
    print(f"\tKeywords EN: {metadata[8]}")
    print(f"\tKeywords PT: {metadata[9]}")
    print(f"\tImage: {metadata[10]}")
    print(f"\tWidth: {metadata[11]}")
    print(f"\tHeight: {metadata[12]}")
    print(f"\tImage extension: {metadata[13]}")
    print(f"\tDate: {metadata[14]}")
    print("Is this metadata ok? (y/n): ", end='')
    if BYPASS_CHECK_METADATA:
        return True
    answer = input()
    while answer.lower() not in ['y', 'n', 'yes', 'no']:
        print("Please, write 'y' or 'n': ", end='')
        answer = input()
    if answer.lower() == 'y' or answer.lower() == 'yes':
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get metadata from a notebook')
    parser.add_argument('notebook_path', type=str, help='Path to the notebook')
    args = parser.parse_args()
    get_notebook_metadata(args.notebook_path)