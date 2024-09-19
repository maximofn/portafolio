from dotenv import load_dotenv
import os
import google.generativeai as genai
from error_codes import QUOTA_EXCEEDED_ERROR, INTERNAL_ERROR

class Gemini:
    def __init__(self, system_instruction):
        self.model = None
        self.gemini_model_name = "gemini-1.5-pro"
        self.load_gemini_api_key()
        self.create_model(system_instruction)
    
    def load_gemini_api_key(self):
        load_dotenv()
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if GEMINI_API_KEY is None:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=GEMINI_API_KEY)

    def create_model(self, system_instruction):
        self.model = genai.GenerativeModel(
            model_name=self.gemini_model_name,
            system_instruction=system_instruction,
        )
    
    def chat_with_gemini(self, input_text):
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
            else:
                print('Unknown error')
                response = None
            return response
        return response.text
    