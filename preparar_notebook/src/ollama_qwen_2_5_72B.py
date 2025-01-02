from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
import time
import torch
from torch import cosine_similarity
import numpy as np

class Ollama_qwen2_5_72B:
    def __init__(self, system_instruction, system_check, num_checks, temperature=0.7, top_p=0.7, max_tokens=1024):
        self.system_instruction = system_instruction
        self.system_check = system_check
        self.num_checks = num_checks
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.chat_model = ChatOllama(
            model = "qwen2.5:72b",
            temperature = self.temperature,
            num_predict = self.max_tokens,
            top_p = self.top_p,
            stream = False,
        )
        self.embeddings_model = OllamaEmbeddings(
            model = "qwen2.5:72b"
        )
        self.no_ortographyc_errors_text = "No hay errores ortográficos"
        no_ortographyc_errors_embedding = self.embeddings_model.embed_query(self.no_ortographyc_errors_text)
        no_ortographyc_errors_embedding_numpy = np.array(no_ortographyc_errors_embedding)
        self.no_ortographyc_errors_embedding_tensor = torch.tensor(no_ortographyc_errors_embedding_numpy).unsqueeze(0)
        self.chat_error_counter = 0
        self.chat_error_limit = 10
    
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
            print(f'Error ({self.chat_error_counter}): {e}')
            print(f"response: {response}")
            if self.chat_error_counter < self.chat_error_limit:
                self.chat_error_counter += 1
                time.sleep(1)
                return self.check(messages, response, debug=debug)
            else:
                print(f"Translation limit reached")
                self.chat_error_counter = 0
                exit(1)

    def chat(self, input_text, response_raw=False, debug=False):
        try:
            # Construct messages
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

            # Debug messages
            if debug:
                print(f"Type Messages: {type(messages)}, len Messages: {len(messages)}")
                if type(messages) == list:
                    for i, message in enumerate(messages):
                        print(f"\tindex: {i}, Type Message: {type(message)}")
                        if type(message) == dict:
                            for j, (key, value) in enumerate(message.items()):
                                print(f"\t\tindex list: {i}, index dict: {j}, {key}: {value}")
            
            # Chat
            response = self.chat_model.invoke(messages)
            response = response.content
            if debug: print(f"Response type: {type(response)}")
            if debug: print(f"Response: {response}")

            # Get embeddings
            response_embedding = self.embeddings_model.embed_query(response)
            response_embedding_numpy = np.array(response_embedding)
            response_embedding_tensor = torch.tensor(response_embedding_numpy).unsqueeze(0)
            # if debug: print(f"Embedding: {embedding}")

            # Cosine similarity with no ortography errors
            similarity = cosine_similarity(response_embedding_tensor, self.no_ortographyc_errors_embedding_tensor)
            if debug: print(f"Similarity: {similarity}")

            # Check
            for i in range(self.num_checks):
                messages, response = self.check(messages, response, debug=debug)
            return response
        except Exception as e:
            print(f'Error ({self.chat_error_counter}): {e}')
            print(f"response: {response}")
            if self.chat_error_counter < self.chat_error_limit:
                self.chat_error_counter += 1
                time.sleep(1)
                return self.chat(input_text)
            else:
                print(f"Translation limit reached")
                self.chat_error_counter = 0
                exit(1)
        
        if response_raw:
            return response