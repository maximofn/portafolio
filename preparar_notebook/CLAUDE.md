# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python-based Jupyter notebook processing pipeline that prepares notebooks for publication in a portfolio website. The system performs orthographic corrections, translations, HTML conversion, and metadata management for notebooks.

## Core Architecture

### Main Components

1. **Main Pipeline (`src/preparar_notebook.py`)**: Command-line interface that orchestrates the entire notebook preparation process
2. **Notebook Utils (`src/notebook_utils.py`)**: Core `Notebook` class for reading, manipulating, and saving Jupyter notebooks
3. **Utility Functions (`src/utils.py`)**: Common utilities including path resolution and user interaction helpers
4. **Processing Modules**: Specialized modules for each step of the pipeline:
   - `corrections_jupyter_notebook.py`: Orthographic corrections using LLM services
   - `translate_jupyter_notebooks.py`: Translation capabilities
   - `jupyter_notebook_to_html.py`: HTML conversion
   - `get_notebook_metadata.py`: Metadata extraction and validation
   - `add_page_to_its_json_file.py` & `add_page_to_its_sitemap.py`: Website integration

### LLM Integration

The codebase integrates with multiple LLM providers:
- Gemini (`gemini.py`)
- GPT-4o (`gpt4o.py`)
- Groq (`groq_llm.py`)
- Local MLX models (`mlx_qwen_*.py`)
- Ollama models (`ollama_qwen_*.py`)

## Common Commands

### Running the Main Pipeline
```bash
python src/preparar_notebook.py <notebook_path>
```

### Available Options
- `--no_check_metadata`: Skip metadata validation
- `--yes_correct_ortografic_errors`: Auto-correct orthographic errors
- `--yes_translate`: Auto-translate notebook
- `--yes_convert_to_html`: Auto-convert to HTML
- `--yes_add_to_json`: Auto-add to JSON metadata
- `--yes_add_to_sitemap`: Auto-add to sitemap

### Running Tests
```bash
cd tests
python -m unittest discover -v
```

Note: Tests use the standard `unittest` framework. Some tests may take time due to LLM API calls.

### Running Individual Test Files
```bash
python -m unittest tests.test_notebook_utils -v
python -m unittest tests.test_corrections_jupyter_notebook -v
```

## Key Patterns

### Notebook Processing Workflow
1. Extract metadata from notebook
2. Validate metadata completeness
3. Apply orthographic corrections (optional)
4. Translate content (optional)
5. Convert to HTML (optional)
6. Update JSON metadata files (optional)
7. Update sitemap (optional)

### Path Resolution
The system uses a recursive parent directory search to find the "portafolio" folder, implemented in `utils.py:get_portafolio_path()`.

### Error Handling
Error codes are centralized in `error_codes.py`, including quota exceeded errors for LLM services.

## Development Notes

- The codebase follows a modular design where each processing step is a separate module
- Interactive prompts use `utils.ask_for_something()` for consistent user interaction
- The `Notebook` class provides a clean interface for Jupyter notebook manipulation
- LLM corrections are cached to avoid redundant API calls
- The system is designed to work with Spanish content but supports translation workflows