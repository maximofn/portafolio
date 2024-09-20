from tqdm import tqdm
from gemini import Gemini
from notebook import Notebook

TARGET_LANGUAGES = ['en', 'pt']

def translate_jupyter_notebook(notebook_path):
    # load gemini model
    model = Gemini(system_instruction=SYSTEM_INSTRUCTION)

    # Get notebook content as a dictionary
    notebook = Notebook(notebook_path)
    notebook_content_dict = notebook.get_content_as_json()
    cells = notebook.cells()   # Get only with the cells
    total_markdown_cells = notebook.number_markdown_cells()

    # Create a new notebook for each target language
    notebook_en = Notebook(notebook_path, 'en')
    notebook_pt = Notebook(notebook_path, 'pt')
    notebook_en.save_content_dict(notebook_content_dict)
    target_notebooks = [notebook_en, notebook_pt]

    # Iterate for each cell in the notebook
    # print(f"\tCorrections of {notebook_path}")
    # bar = tqdm(cells, bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}')
    # markdown_cell_counter = 0
    # for cell_counter, cell in enumerate(bar):
    #     # if cell_counter == 4:
    #     #     break
    #     if cell['cell_type'] == 'markdown':
    #         if type(cell['source']) == str:
    #             cell['source'] = apply_corrections(model, cell['source'])
    #         elif type(cell['source']) == list:
    #             for number_line, line in enumerate(cell['source']):
    #                 cell['source'][number_line] = apply_corrections(model, line)
    #         markdown_cell_counter += 1
    #     bar.set_description(f"\t\tCell {markdown_cell_counter}/{total_markdown_cells}")
    # print(f"\tEnd of translation")

    # Save translated notebooks
    notebook.save_cells(cells)