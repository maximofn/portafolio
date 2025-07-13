from dotenv import load_dotenv
import os
from groq import Groq

class Groq_llama3_1_70B:
    def __init__(self, system_instruction, temperature=1, top_p=1, max_tokens=1024, stream=False, stop=None):
        self.model = None
        self.GRPQ_API_KEY = None
        self.groq_model = "llama-3.1-70b-versatile"
        self.load_api_key()
        self.client = Groq(api_key=self.GRPQ_API_KEY)
        self.system_instruction = system_instruction
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.stream = stream
        self.stop = stop
    
    def load_api_key(self):
        load_dotenv()
        self.GRPQ_API_KEY = os.getenv("GRPQ_API_KEY")
        if self.GRPQ_API_KEY is None:
            raise ValueError("GRPQ_API_KEY is not set")
    
    def chat(self, input_text, response_raw=False, debug=False):
        completion = self.client.chat.completions.create(
            model=self.groq_model,
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
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            stream=self.stream,
            stop=self.stop,
        )
        if response_raw:
            return completion
        
        finish_reason = completion.choices[0].finish_reason
        if finish_reason == "stop":
            message_content = completion.choices[0].message.content
            return message_content
        elif finish_reason == "length":
            return "Incomplete model output because of the max_tokens parameter or the token limit"


if __name__ == "__main__":
    system_instruction = """
        Eres un experto corrector de texto markdown. Tu misión es corregir ortograficamente texto markdown.

        Enfoque en la corrección: Por favor, revisa el siguiente texto y corrige únicamente los errores ortográficos, sin modificar la estructura, el estilo ni el contenido.
        No hagas cambios del tipo 'Con estos modelos podemos hacer...' a 'Con estos modelos se puede hacer...', tampoco quiero cambios del tipo 'Podemos obtener la longitud de nuestro string mediante la función `len()`' a 'Podemos obtener la longitud de nuestro string mediante la función `len()`.' es decir, no añadas puntos al final de la oración, solo corrige si hay errores de ortografía.

        Te van a pasar textos markdown y tienes que corregirlos ortograficamente en español. Responde solo con la corrección, responde con el texto que hay y la corrección que sugieres.

        El formato de salida tiene que ser un json con llaves llamadas `original`, otra `correccion` y la última será `explicación` con la explicación de qué cambia y por qué. Si no hay errores ortográficos responde ese json con las llaves vacías. Es decir será un json así:
        ```
        {
            "original": "",
            "correccion": "",
            "explicación": ""
        }
        ```

        Recuerda, rellena el json solo con los textos markdown que tienen errores, no pongas en el json los que no tienen errores y no quiero que añadir un punto al final de la oración sea una corrección
    """
    groq_llm = Groq_llama3_1_70B(system_instruction=system_instruction)
    response = groq_llm.chat("Ayer vajé por la montaña", response_raw=True)
    print(response)

    response_id = response.id
    print(f"response_id: {response_id}", end="\n\n")

    print(f"type(response.choices[0]): {type(response.choices[0])}")
    print(f"response.choices[0]: {response.choices[0]}", end="\n\n")
    # Choice(
    #   finish_reason='stop', 
    #   index=0, 
    #   logprobs=None, 
    #   message=ChatCompletionMessage(
    #       content='```json\n{\n    "original": "Ayer vajé por la montaña",\n    "correccion": "Ayer viajé por la montaña",\n    "explicación": "La palabra \'vajé\' está incorrecta, la forma correcta es \'viajé\'."\n}\n```', 
    #       refusal=None, 
    #       role='assistant', 
    #       function_call=None, 
    #       tool_calls=None
    #   ), 
    #   content_filter_results={
    #       'hate': {
    #           'filtered': False, 
    #           'severity': 'safe'
    #       }, 
    #       'self_harm': {
    #           'filtered': False, 
    #           'severity': 'safe'
    #       }, 
    #       'sexual': {
    #           'filtered': False, 
    #           'severity': 'safe'
    #       }, 
    #       'violence': {
    #           'filtered': False, 
    #           'severity': 'safe'
    #       }
    #   }
    finish_reason = response.choices[0].finish_reason
    index = response.choices[0].index
    logprobs = response.choices[0].logprobs
    message = response.choices[0].message
    message_content = message.content
    # message_refusal = message.refusal
    message_role = message.role
    message_function_call = message.function_call
    message_tool_calls = message.tool_calls
    # content_filter_results = response.choices[0].content_filter_results
    print(f"finish_reason: {finish_reason}")
    print(f"index: {index}")
    print(f"logprobs: {logprobs}")
    print(f"message: {message}")
    print(f"message_content: {message_content}")
    # print(f"message_refusal: {message_refusal}")
    print(f"message_role: {message_role}")
    print(f"message_function_call: {message_function_call}")
    print(f"message_tool_calls: {message_tool_calls}")
    # print(f"content_filter_results: {content_filter_results}")

