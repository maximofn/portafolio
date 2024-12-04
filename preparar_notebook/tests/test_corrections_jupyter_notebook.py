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
