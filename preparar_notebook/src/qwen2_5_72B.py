from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient
import time

class Qwen2_5_72B:
    def __init__(self, system_instruction, system_check, num_checks, temperature=0.7, top_p=0.7, max_tokens=1024):
        self.model = "Qwen/Qwen2.5-72B-Instruct"
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
    
    def check(self, messages, response, debug=False):
        try:
            messages.append({"role": "assistant", "content": response}) # add response to messages
            messages.append({"role": "system", "content": self.system_check}) # add self.system_check to messages
            if debug: 
                print(f"\n(check) Type Messages: {type(messages)}, len Messages: {len(messages)}")
                if type(messages) == list:
                    for i, message in enumerate(messages):
                        print(f"\tindex: {i}, Type Message: {type(message)}")
                        if type(message) == dict:
                            for j, (key, value) in enumerate(message.items()):
                                print(f"\t\tindex list: {i}, index dict: {j}, {key}: {value}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages, 
                stream=False, 
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            response = response.choices[0].message.content
            if debug: print(f"(check) Response: {response}")
            return messages, response
        except Exception as e:
            print(f'Error ({self.translation_counter}): {e}')
            print(f"response: {response}")
            if self.translation_counter < self.translation_limit:
                self.translation_counter += 1
                time.sleep(1)
                return self.check(messages, response, debug=debug)
            else:
                print(f"Translation limit reached")
                self.translation_counter = 0
                exit(1)

    def chat(self, input_text, response_raw=False, debug=False):
        try:
            messages = [
                {
                    "role": "system",
                    "content": self.system_instruction
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ]
            if debug:
                print(f"Type Messages: {type(messages)}, len Messages: {len(messages)}")
                if type(messages) == list:
                    for i, message in enumerate(messages):
                        print(f"\tindex: {i}, Type Message: {type(message)}")
                        if type(message) == dict:
                            for j, (key, value) in enumerate(message.items()):
                                print(f"\t\tindex list: {i}, index dict: {j}, {key}: {value}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages, 
                stream=False, 
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
            )
            response = response.choices[0].message.content
            if debug: print(f"Response: {response}")
            for i in range(self.num_checks):
                messages, response = self.check(messages, response, debug=debug)
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