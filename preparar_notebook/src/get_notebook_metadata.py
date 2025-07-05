import argparse
import json
from PIL import Image
import os
from utils import get_portafolio_path, get_pwd_path, ask_for_something
import requests
from io import BytesIO

BYPASS_CHECK_METADATA = False

MAXIMO_FN_KEY = 'maximofn'

WEB_PORTFOLIO_PATH = 'portfolio'    # portfolio not portAfolio
WEB_PUBLIC_PATH = 'public'

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
IMAGE_HOVER_PATH_KEY = 'image_hover_path'
DATE_KEY = 'date'



def get_image_width_height(image_path):
    # Open image and get width and height
    try:
        with Image.open(BytesIO(requests.get(image_path).content)) as img:
            width, height = img.size
    except:
        print(f'Error opening image {image_path}')
        exit(1)
    return width, height

def get_image_extension(image_path):
    if '.' in image_path:
        return image_path.split('.')[-1]
    else:
        print(f'No extension found in {image_path}')
        exit(1)

def get_notebook_metadata(notebook_path):
    with open(notebook_path, 'r') as f:
        notebook_json = json.load(f)
    
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
    image_hover_path = None
    witdh = None
    height = None
    image_extension = None
    date = None

    metadata = notebook_json.get('metadata', {})

    if MAXIMO_FN_KEY in metadata.keys():
        is_title_es_in_metadata = TITLE_ES_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_title_en_in_metadata = TITLE_EN_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_title_pt_in_metadata = TITLE_PT_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_end_url_in_metadata = END_URL_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_description_es_in_metadata = DESCRIPTION_ES_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_description_en_in_metadata = DESCRIPTION_EN_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_description_pt_in_metadata = DESCRIPTION_PT_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_keywords_es_in_metadata = KEYWORDS_ES_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_keywords_en_in_metadata = KEYWORDS_EN_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_keywords_pt_in_metadata = KEYWORDS_PT_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_image_in_metadata = IMAGE_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_image_hover_path_in_metadata = IMAGE_HOVER_PATH_KEY in metadata[MAXIMO_FN_KEY].keys()
        is_date_in_metadata = DATE_KEY in metadata[MAXIMO_FN_KEY].keys()

        if is_title_es_in_metadata and is_title_en_in_metadata and is_title_pt_in_metadata and is_end_url_in_metadata and \
            is_description_es_in_metadata and is_description_en_in_metadata and is_description_pt_in_metadata and \
            is_keywords_es_in_metadata and is_keywords_en_in_metadata and is_keywords_pt_in_metadata and \
            is_image_in_metadata and is_image_hover_path_in_metadata and is_date_in_metadata:
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
                image_hover_path = metadata[MAXIMO_FN_KEY][IMAGE_HOVER_PATH_KEY]
                witdh, height = get_image_width_height(image)
                image_extension = get_image_extension(image)
                date = metadata[MAXIMO_FN_KEY][DATE_KEY]
        
        else:
            print('Some metadata keys are missing')
            if not is_title_es_in_metadata: print(f'\tNo {TITLE_ES_KEY} key in metadata')
            if not is_title_en_in_metadata: print(f'\tNo {TITLE_EN_KEY} key in metadata')
            if not is_title_pt_in_metadata: print(f'\tNo {TITLE_PT_KEY} key in metadata')
            if not is_end_url_in_metadata: print(f'\tNo {END_URL_KEY} key in metadata')
            if not is_description_es_in_metadata: print(f'\tNo {DESCRIPTION_ES_KEY} key in metadata')
            if not is_description_en_in_metadata: print(f'\tNo {DESCRIPTION_EN_KEY} key in metadata')
            if not is_description_pt_in_metadata: print(f'\tNo {DESCRIPTION_PT_KEY} key in metadata')
            if not is_keywords_es_in_metadata: print(f'\tNo {KEYWORDS_ES_KEY} key in metadata')
            if not is_keywords_en_in_metadata: print(f'\tNo {KEYWORDS_EN_KEY} key in metadata')
            if not is_keywords_pt_in_metadata: print(f'\tNo {KEYWORDS_PT_KEY} key in metadata')
            if not is_image_in_metadata: print(f'\tNo {IMAGE_KEY} key in metadata')
            if not is_image_hover_path_in_metadata: print(f'\tNo {IMAGE_HOVER_PATH_KEY} key in metadata')
            if not is_date_in_metadata: print(f'\tNo {DATE_KEY} key in metadata')

    else:
        print(f'No {MAXIMO_FN_KEY} key in metadata')

    return title_es, title_en, title_pt, end_url, description_es, description_en, description_pt, \
        keywords_es, keywords_en, keywords_pt, image, image_hover_path, witdh, height, image_extension, date

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
    print(f"\tImage hover path: {metadata[11]}")
    print(f"\tWidth: {metadata[12]}")
    print(f"\tHeight: {metadata[13]}")
    print(f"\tImage extension: {metadata[14]}")
    print(f"\tDate: {metadata[15]}")
    if BYPASS_CHECK_METADATA:
        return True
    if ask_for_something("Is this metadata ok? (y/n)", ['y', 'yes'], ['n', 'no']):
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get metadata from a notebook')
    parser.add_argument('notebook_path', type=str, help='Path to the notebook')
    args = parser.parse_args()
    get_notebook_metadata(args.notebook_path)