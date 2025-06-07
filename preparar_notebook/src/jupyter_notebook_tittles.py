import json

def extract_titles(notebook_path):
    """
    Extracts titles and their levels from a Jupyter Notebook.

    Args:
        notebook_path (str): The path to the Jupyter Notebook file.

    Returns:
        list: A list of dictionaries, where each dictionary contains
              'text' (the title string) and 'level' (e.g., 'h1', 'h2').
              Returns an empty list if an error occurs.
    """
    titles = []
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)

        for cell in notebook_content.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                # Ensure source is iterable and handle None case
                cell_source = cell.get('source') or []
                for item in cell_source: # item can be a string or a list of strings (though typically a string)
                    # Ensure item is a string before calling splitlines
                    if isinstance(item, str):
                        for line in item.splitlines():
                            line_stripped = line.lstrip()
                            if line_stripped.startswith('#'):
                                level = 0
                                for char in line_stripped:
                                    if char == '#':
                                        level += 1
                                    else:
                                        break
                                # Ensure there's a space after the hashes
                                if level > 0 and len(line_stripped) > level and line_stripped[level] == ' ':
                                    title_text = line_stripped[level:].strip() # Use strip() for cleaner text
                                    if title_text: # Ensure title is not empty
                                        titles.append({'text': title_text, 'level': f'h{level}'})
    except FileNotFoundError:
        print(f"Error: File not found at {notebook_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {notebook_path}")
        return []
    return titles

if __name__ == '__main__':
    # Test with a dummy notebook expected to be in the same directory
    dummy_notebook_path = 'dummy_notebook.ipynb'
    # Attempt to create a dummy notebook for testing if it doesn't exist
    # (this is simplified for the subtask; ideally, the file is pre-created)
    import os
    if not os.path.exists(dummy_notebook_path):
        print(f"Warning: Dummy notebook {dummy_notebook_path} not found. Test might not run as expected.")
        # In a real scenario, you might skip the test or ensure the file is created.
        # For this subtask, we assume the file creation step (1) is done by the subtask runner.

    print(f"Extracting titles from: {dummy_notebook_path}")
    titles = extract_titles(dummy_notebook_path)
    if titles:
        print("Extracted titles:")
        for title in titles:
            print(f"- Level: {title['level']}, Text: {title['text']}")
    else:
        print("No titles extracted or an error occurred.")

    # Test with a non-existent notebook
    print("\nExtracting titles from: non_existent_notebook.ipynb")
    titles_non_existent = extract_titles("non_existent_notebook.ipynb")
    if titles_non_existent:
        print("Extracted titles:")
        for title in titles_non_existent:
            print(f"- Level: {title['level']}, Text: {title['text']}")
    else:
        print("No titles extracted or an error occurred (as expected for a non-existent file).")
