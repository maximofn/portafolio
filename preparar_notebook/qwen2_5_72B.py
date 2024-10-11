from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
import time

class Qwen2_5_72B:
    def __init__(self, system_instruction, temperature=0.7, top_p=0.7, max_tokens=1024):
        self.model = "Qwen/Qwen2.5-72B-Instruct"
        self.HUGGING_FACE_TOKEN = None
        self.load_api_key()
        self.client = InferenceClient(api_key=self.HUGGING_FACE_TOKEN)
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.translation_counter = 0
        self.translation_limit = 10
    
    def load_api_key(self):
        load_dotenv()
        self.HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")
        if self.HUGGING_FACE_TOKEN is None:
            raise ValueError("HUGGING_FACE_TOKEN is not set")

    def chat(self, input_text, response_raw=False):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_instruction
                    },
                    {
                        "role": "user",
                        "content": input_text
                    }
                ], 
                stream=False, 
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            # for chunk in response:
            #     print(chunk.choices[0].delta.content)
        except Exception as e:
            print(f'Error ({self.translation_counter}): {e}')
            if self.translation_counter < self.translation_limit:
                self.translation_counter += 1
                time.sleep(1)
                return self.chat(input_text)
            else:
                print(f"Translation limit reached")
                self.translation_counter = 0
        
        if response_raw:
            return response