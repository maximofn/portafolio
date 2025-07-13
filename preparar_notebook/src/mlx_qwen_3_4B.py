try:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
except:
    print("MLX_Qwen3_4B not found")
    # exit(1)

import time

class MLX_Qwen3_4B:
    def __init__(self, system_instruction, system_check, num_checks, temperature=0.7, top_p=0.7, max_tokens=1024):
        self.system_instruction = system_instruction
        self.system_check = system_check
        self.num_checks = num_checks
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        
        self.model, self.tokenizer = load("mlx-community/Qwen3-4B-4bit-DWQ-053125")
        self.chat_error_counter = 0
        self.chat_error_limit = 10
    
    def check(self, messages, response, debug=False):
        try:
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "system", "content": self.system_check})
            
            if debug:
                print(f"\\n(check) Messages going into template generation:")
                for msg in messages:
                    print(f"\\t- {msg['role']}: {msg['content'][:80]}...")

            prompt = self.tokenizer.apply_chat_template(
                messages, 
                add_generation_prompt=True,
            )
            
            # Generate a new response from the model based on the updated conversation.
            new_response = generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                # temperature=self.temperature,
                max_tokens=self.max_tokens,
                # top_p=self.top_p,
                verbose=debug
            )
            
            if debug: print(f"(check) Response: {new_response}")

            # Return the updated message history and the new, revised response.
            return messages, new_response
        except Exception as e:
            # This is our error handling block. If something goes wrong, it will 'catch' the exception.
            print(f'Error in check ({self.chat_error_counter}): {e}')
            print(f"response: {response}")
            # We will retry the operation a few times before giving up.
            if self.chat_error_counter < self.chat_error_limit:
                self.chat_error_counter += 1
                time.sleep(1) # Wait for a second before retrying.
                return self.check(messages, response, debug=debug)
            else:
                print(f"Check limit reached")
                self.chat_error_counter = 0
                exit(1) # Exit the script if it fails too many times.

    # The chat method is the main function to interact with the model.
    def chat(self, input_text, debug=False):
        try:
            # Construct the initial messages list with the main system instruction and the user's input.
            messages = [
                {"role": "system", "content": self.system_instruction},
                {"role": "user", "content": input_text}
            ]

            if debug:
                print(f"Initial messages:")
                for msg in messages:
                    print(f"\\t- {msg['role']}: {msg['content']}")
            
            # Apply the chat template to format the initial prompt.
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                add_generation_prompt=True,
            )

            # Generate the initial response from the model.
            sampler = make_sampler(temp=self.temperature, top_p=self.top_p)
            response = generate(
                self.model, 
                self.tokenizer, 
                prompt=prompt, 
                max_tokens=self.max_tokens,
                sampler=sampler,
                verbose=debug
            )

            if debug: print(f"Initial Response: {response}")

            # This loop performs the self-correction checks.
            # It will run 'self.num_checks' times.
            for i in range(self.num_checks):
                if debug: print(f"\\n--- Starting check {i+1}/{self.num_checks} ---")
                messages, response = self.check(messages, response, debug=debug)

            # Return the final, corrected response.
            return response
        except Exception as e:
            # Error handling for the main chat function.
            print(f'Error in chat ({self.chat_error_counter}): {e}')
            # 'locals()' is a dictionary of local variables. We check if 'response' exists before printing.
            if 'response' in locals():
                print(f"response: {response}")
            if self.chat_error_counter < self.chat_error_limit:
                self.chat_error_counter += 1
                time.sleep(1)
                # We use recursion to retry the chat function.
                return self.chat(input_text, debug=debug)
            else:
                print(f"Chat limit reached")
                self.chat_error_counter = 0
                exit(1)
