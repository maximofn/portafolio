import argparse
import json
from PIL import Image

def get_image_width_height(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height

def get_image_extension(image_path):
    return image_path.split('.')[-1]

def get_notebook_metadata(notebook_path):
    with open(notebook_path, 'r') as f:
        notebook = json.load(f)
    
    title = "none"
    end_url = "none"
    description_es = "none"
    description_en = "none"
    description_pt = "none"
    keywords_es = "none"
    keywords_en = "none"
    keywords_pt = "none"
    image = "none"
    date = "none"

    metadata = notebook.get('metadata', {})
    if 'maximofn' in metadata.keys():
        if ('title' in metadata['maximofn'].keys()) and \
            ('end_url' in metadata['maximofn'].keys()) and \
            ('description_es' in metadata['maximofn'].keys()) and \
            ('description_en' in metadata['maximofn'].keys()) and \
            ('description_pt' in metadata['maximofn'].keys()) and \
            ('keywords_es' in metadata['maximofn'].keys()) and \
            ('keywords_en' in metadata['maximofn'].keys()) and \
            ('keywords_pt' in metadata['maximofn'].keys()) and \
            ('image' in metadata['maximofn'].keys()) and \
            ('date' in metadata['maximofn'].keys()):
                title = metadata['maximofn']['title']
                end_url = metadata['maximofn']['end_url']
                description_es = metadata['maximofn']['description_es']
                description_en = metadata['maximofn']['description_en']
                description_pt = metadata['maximofn']['description_pt']
                keywords_es = metadata['maximofn']['keywords_es']
                keywords_en = metadata['maximofn']['keywords_en']
                keywords_pt = metadata['maximofn']['keywords_pt']
                image = metadata['maximofn']['image']
                witdh, height = get_image_width_height(image)
                image_extension = get_image_extension(image)
                date = metadata['maximofn']['date']
        
        else:
            print('Some metadata keys are missing')

    else:
        print('No maximofn key in metadata')

    return_string = ""
    return_string += f"{title}$"
    return_string += f"{end_url}$"
    return_string += f"{description_es}$"
    return_string += f"{description_en}$"
    return_string += f"{description_pt}$"
    return_string += f"{keywords_es}$"
    return_string += f"{keywords_en}$"
    return_string += f"{keywords_pt}$"
    return_string += f"{image}$"
    return_string += f"{witdh}$"
    return_string += f"{height}$"
    return_string += f"{image_extension}$"
    return_string += f"{date}$"
    print(return_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get metadata from a notebook')
    parser.add_argument('notebook_path', type=str, help='Path to the notebook')
    args = parser.parse_args()
    get_notebook_metadata(args.notebook_path)