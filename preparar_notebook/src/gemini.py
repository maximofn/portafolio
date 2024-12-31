from dotenv import load_dotenv
import os
import google.generativeai as genai
from error_codes import QUOTA_EXCEEDED_ERROR, INTERNAL_ERROR, API_KEY_ERROR

GEMINI_MODEL_NAME = "gemini-2.0-flash-exp"

class Gemini:
    def __init__(self, system_instruction, temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192, response_mime_type="text/plain"):
        self.model = None
        self.gemini_model_name = GEMINI_MODEL_NAME
        self.load_gemini_api_key()
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_output_tokens = max_output_tokens
        self.response_mime_type = response_mime_type
        self.create_model(system_instruction)
    
    def load_gemini_api_key(self):
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY is None:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=GEMINI_API_KEY)

    def create_model(self, system_instruction):
        generation_config = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
            "response_mime_type": self.response_mime_type,
        }
        self.model = genai.GenerativeModel(
            model_name=self.gemini_model_name,
            system_instruction=system_instruction,
            generation_config=generation_config
        )
    
    def chat(self, input_text):
        try:
            response = self.model.generate_content(input_text)
        except Exception as e:
            print(f'Error: {e}')
            if str(QUOTA_EXCEEDED_ERROR) in str(e):
                print('Quota exceeded')
                response = QUOTA_EXCEEDED_ERROR
            elif str(INTERNAL_ERROR) in str(e):
                print('Internal error')
                response = INTERNAL_ERROR
            elif str(API_KEY_ERROR) in str(e):
                print('API key error')
                response = API_KEY_ERROR
            else:
                print('Unknown error')
                response = None
            return response
        return response.text
    