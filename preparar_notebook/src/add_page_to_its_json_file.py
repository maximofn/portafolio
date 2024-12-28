from pathlib import Path
import json

def add_page_to_its_json_file_from_metadata(metadata, notebook_path):
    debug = False

    title_es = metadata[0]
    title_en = metadata[1]
    title_pt = metadata[2]
    end_url = metadata[3]
    description_es = metadata[4]
    description_en = metadata[5]
    description_pt = metadata[6]
    keywords_es = metadata[7]
    keywords_en = metadata[8]
    keywords_pt = metadata[9]
    image = metadata[10]
    image_hover_path = metadata[11]
    width = metadata[12]
    height = metadata[13]
    image_extension = metadata[14]
    date = metadata[15]

    if debug: print(f"Notebook path: {notebook_path}")

    # json file path
    json_file_path = Path(notebook_path).parent.parent / "portfolio"
    if "posts" in str(notebook_path).lower():
        json_file_path = json_file_path / "last_posts.json"
    elif "tips" in str(notebook_path).lower():
        json_file_path = json_file_path / "last_tips.json"
    else: 
        print(f"Unknown notebook path: {notebook_path}")
        exit(1)
    if debug: print(f"JSON file path: {json_file_path}")

    # Read the json file
    with open(json_file_path, "r") as file:
        data = json.load(file)
    last_post_keys_list = list(data['last_posts'].keys())
    last_post = last_post_keys_list[-1]
    last_post_number = int(last_post.replace("post", ""))
    if debug: print(f"last_post_number: {last_post_number}")

    # Create the post to add dictionary
    post_to_add_dict = {
        "title": {
            "es": title_es,
            "en": title_en,
            "pt": title_pt
        },
        "description": {
            "es": description_es,
            "en": description_en,
            "pt": description_pt
        },
        "image_path": {
            "es": image,
            "en": image,
            "pt": image
        },
        "image_hover_path": {
            "es": image_hover_path,
            "en": image_hover_path,
            "pt": image_hover_path
        },
        "post_link": {
            "es": end_url,
            "en": end_url,
            "pt": end_url
        }
    }

    # Add the post to the json file
    data['last_posts'][f"post{last_post_number + 1}"] = post_to_add_dict

    # Write to the json file
    with open(json_file_path, "w") as file:
        json.dump(data, file, indent=4)
