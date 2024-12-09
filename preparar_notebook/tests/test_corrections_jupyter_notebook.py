from unittest.mock import patch
import unittest
import sys
import os
# add path src to sys path
src_path = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+os.path.sep+"src")
sys.path.append(src_path)
from gemini import Gemini
from gpt4o import GPT4o
from groq_llm import Groq_llama3_1_70B
from qwen2_5_72B import Qwen2_5_72B
from corrections_jupyter_notebook import SYSTEM_INSTRUCTION, SYSTEM_CHECK, NUMBER_OF_CHECKS, MODEL, GEMINI_LLM, GPT4O_LLM, GROQ_LLM, QWEN_2_5_72B
from corrections_jupyter_notebook import apply_corrections

class Test_corrections_jupyter_notebook(unittest.TestCase):
    def setUp(self):
        if MODEL == GEMINI_LLM:
            self.model = Gemini(system_instruction=SYSTEM_INSTRUCTION)
        elif MODEL == GPT4O_LLM:
            self.model = GPT4o(system_instruction=SYSTEM_INSTRUCTION)
        elif MODEL == GROQ_LLM:
            self.model = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION)
        elif MODEL == QWEN_2_5_72B:
            self.model = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION, system_check=SYSTEM_CHECK, num_checks=NUMBER_OF_CHECKS)

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections(self, mock_stdout, mock_input):
        line = "La capital de España es Madrid, pero no es la capital de Francia. Sin embargo, la capital de Francia es larís."
        result = apply_corrections(self.model, line)
        self.assertEqual(result, "La capital de España es Madrid, pero no es la capital de Francia. Sin embargo, la capital de Francia es París.")

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_empty_line(self, mock_stdout, mock_input):
        line = ""
        result = apply_corrections(self.model, line)
        self.assertEqual(result, line)

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_space_line(self, mock_stdout, mock_input):
        line = " "
        result = apply_corrections(self.model, line)
        self.assertEqual(result, line)

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_tab_line(self, mock_stdout, mock_input):
        line = "\t"
        result = apply_corrections(self.model, line)
        self.assertEqual(result, line)

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_return_line(self, mock_stdout, mock_input):
        line = "\n"
        result = apply_corrections(self.model, line)
        self.assertEqual(result, line)

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_example1(self, mock_stdout, mock_input):
        line = "Vamos a probar ahora esta función de embeddings en local"
        result = apply_corrections(self.model, line)
        self.assertEqual(result, "Vamos a probar ahora esta función de embeddings en local")

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_example2(self, mock_stdout, mock_input):
        line = "Para hacer todas estas pruebas me he descargado el dataset [aws-case-studies-and-blogs](https://www.kaggle.com/datasets/harshsinghal/aws-case-studies-and-blogs) y lo he dejado en la carpeta `rag-txt_dataset`, con los siguientes comandos te digo cómo descargarlo y descomprimirlo"
        result = apply_corrections(self.model, line)
        self.assertEqual(result, "Para hacer todas estas pruebas me he descargado el dataset [aws-case-studies-and-blogs](https://www.kaggle.com/datasets/harshsinghal/aws-case-studies-and-blogs) y lo he dejado en la carpeta `rag-txt_dataset`, con los siguientes comandos te digo cómo descargarlo y descomprimirlo")

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_example3(self, mock_stdout, mock_input):
        line = "A crear los `chunk`s!"
        result = apply_corrections(self.model, line)
        self.assertEqual(result, "A crear los `chunk`s!")

    @patch('builtins.input', return_value='y')   # Mock the input to avoid asking for input
    @patch('sys.stdout')    # Mock the stdout to avoid printing to the console
    def test_apply_corrections_example4(self, mock_stdout, mock_input):
        line = "Volvemos a recordar, este modelo de embeddings es muy pequeño, solo 22M de parámetros, por lo que casi en cualquier ordenador se puede ejecutar, más rápido o más lento, pero se puede."
        result = apply_corrections(self.model, line)
        self.assertEqual(result, "Volvemos a recordar, este modelo de embeddings es muy pequeño, solo 22M de parámetros, por lo que casi en cualquier ordenador se puede ejecutar, más rápido o más lento, pero se puede ejecutar.")
