from unittest.mock import patch
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from translate_jupyter_notebooks import translate_text
from translate_jupyter_notebooks import GEMINI_LLM, GPT4o_LLM, GROQ_LLM, QWEN_2_5_72B, LLAMA_3_3_70B, TRANSLATOR_MODEL
from translate_jupyter_notebooks import SYSTEM_INSTRUCTION_EN, SYSTEM_INSTRUCTION_PT, SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, SYSTEM_INSTRUCTION_NOTEBOOK_TRANSLATION_CHECKER
from translate_jupyter_notebooks import NUMBER_OF_PHRASE_CHECKS, NUMBER_OF_NOTEBOOK_CHECKS
from gemini import Gemini
from gpt4o import GPT4o
from groq_llm import Groq_llama3_1_70B
from qwen2_5_72B import Qwen2_5_72B
from llama_3_3_70B import Llama_3_3_70B

PASS_TESTS = False

if not PASS_TESTS:
    class Test_translate_jupyter_notebooks(unittest.TestCase):
        def setUp(self):
            pass
        def test_translate_text_without_text(self):
            pass
        def test_translate_text_with_space(self):
            pass
        def test_translate_text_with_tab(self):
            pass
        def test_translate_text_from_spanish_to_english(self):
            pass
        def test_translate_text_from_spanish_to_portuguese(self):
            pass
else:
    class Test_translate_jupyter_notebooks(unittest.TestCase):
        def setUp(self):
            if TRANSLATOR_MODEL == GEMINI_LLM:
                translator_model_en = Gemini(system_instruction=SYSTEM_INSTRUCTION_EN)
                translator_model_pt = Gemini(system_instruction=SYSTEM_INSTRUCTION_PT)
            elif TRANSLATOR_MODEL == GPT4o_LLM:
                translator_model_en = GPT4o(system_instruction=SYSTEM_INSTRUCTION_EN)
                translator_model_pt = GPT4o(system_instruction=SYSTEM_INSTRUCTION_PT)
            elif TRANSLATOR_MODEL == GROQ_LLM:
                translator_model_en = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_EN)
                translator_model_pt = Groq_llama3_1_70B(system_instruction=SYSTEM_INSTRUCTION_PT)
            elif TRANSLATOR_MODEL == QWEN_2_5_72B:
                translator_model_en = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_EN, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_PHRASE_CHECKS)
                translator_model_pt = Qwen2_5_72B(system_instruction=SYSTEM_INSTRUCTION_PT, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_PHRASE_CHECKS)
            elif TRANSLATOR_MODEL == LLAMA_3_3_70B:
                translator_model_en = Llama_3_3_70B(system_instruction=SYSTEM_INSTRUCTION_EN, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_PHRASE_CHECKS)
                translator_model_pt = Llama_3_3_70B(system_instruction=SYSTEM_INSTRUCTION_PT, system_check=SYSTEM_INSTRUCTION_PHRASE_TRANSLATION_CHECKER, num_checks=NUMBER_OF_PHRASE_CHECKS)
            self.translations_models = [translator_model_en, translator_model_pt]

        def test_translate_text_without_text(self):
            text = ""
            correct_translated_text = text
            translated_text = translate_text(self.translations_models[0], text)
            self.assertEqual(translated_text, correct_translated_text)
        
        def test_translate_text_with_tab(self):
            text = "\t"
            correct_translated_text = text
            translated_text = translate_text(self.translations_models[0], text)
            self.assertEqual(translated_text, correct_translated_text)
        
        def test_translate_text_from_spanish_to_english(self):
            text = "Hola, ¿cómo estás?"
            response = "Hello, how are you?"
            translated_text = translate_text(self.translations_models[0], text)
            if translated_text[-1] == "\n":
                translated_text = translated_text[:-1]
            self.assertEqual(translated_text, response)
        
        def test_translate_text_from_spanish_to_portuguese(self):
            text = "Hola, ¿cómo estás?"
            response = "Olá, como estás?"
            translated_text = translate_text(self.translations_models[1], text)
            if translated_text[-1] == "\n":
                translated_text = translated_text[:-1]
            self.assertEqual(translated_text, response)
