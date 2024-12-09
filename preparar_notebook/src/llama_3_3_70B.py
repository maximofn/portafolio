from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
import time

class Llama_3_3_70B:
    def __init__(self, system_instruction, system_check, num_checks, temperature=0.7, top_p=0.7, max_tokens=1024):
        self.model = "meta-llama/Llama-3.3-70B-Instruct"
        self.HUGGING_FACE_TOKEN = None
        self.load_api_key()
        self.client = InferenceClient(api_key=self.HUGGING_FACE_TOKEN)
        self.system_instruction = system_instruction
        self.system_check = system_check
        self.num_checks = num_checks
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
    
    def check(self, input_text, response):
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
                        "content": self.system_check + "\nlo que te he dado: \n```" + input_text + "\n```\nlo que has respondido: \n```" + response + "\n```"
                    }
                ], 
                stream=False, 
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f'Error ({self.translation_counter}): {e}')
            print(f"response: {response}")
            if self.translation_counter < self.translation_limit:
                self.translation_counter += 1
                time.sleep(1)
                return self.check(input_text)
            else:
                print(f"Translation limit reached")
                self.translation_counter = 0
                exit(1)

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
            response = response.choices[0].message.content
            for i in range(self.num_checks):
                response = self.check(input_text, response)
            return response
        except Exception as e:
            print(f'Error ({self.translation_counter}): {e}')
            print(f"response: {response}")
            if self.translation_counter < self.translation_limit:
                self.translation_counter += 1
                time.sleep(1)
                return self.chat(input_text)
            else:
                print(f"Translation limit reached")
                self.translation_counter = 0
                exit(1)
        
        if response_raw:
            return response