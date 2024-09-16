import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import argparse
from error_codes import QUOTA_EXCEEDED_ERROR
from get_notebook_metadata import get_portafolio_path
from sentence_transformers import SentenceTransformer
import torch
from torch.nn.functional import cosine_similarity

print("Loading encoder model...")
encoder_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
encoder_model.eval()
print("Encoder model loaded")

SIMILARITY_THRESHOLD = 0.9

def load_gemini_api_key():
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY is None:
        raise ValueError("GEMINI_API_KEY is not set")
    genai.configure(api_key=GEMINI_API_KEY)

def create_model():
    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings # See https://ai.google.dev/gemini-api/docs/safety-settings
        system_instruction="Eres un experto corrector de jupyter notebooks. Tu misión es corregir ortograficamente jupyter notebooks.\n\nEnfoque en la corrección: Por favor, revisa el siguiente texto y corrige únicamente los errores ortográficos, sin modificar la estructura, el estilo ni el contenido. No hagas cambios del tipo cambies 'Con estos modelos podemos hacer...' a 'Con estos modelos se puede hacer...', solo corrige si hay errores de ortografía.\n\nTe van a pasar jupyter notebooks y tienes que corregirlos ortograficamente en español. Ten en cuenta que las celdas de código no hay que corregirlas. Responde solo con las celdas que tienen errores ortograficos, responde con el texto que hay y la corrección que sugieres.\n\nEl formato de salida tiene que ser un json con llaves llamadas `correccionX` donde `X` será un número que comenzará desde 0 e irá incrementando. Dentro de cada corrección habrá otras tres llaves, una será `original`, otra `correccion` y la última será `explicación` con la explicación de qué cambia y por qué\n\nRecuerda, rellena el json solo con las celdas que tienen errores, no pongas en el json las que no tienen errores",
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "{\n \"cells\": [\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"# DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Aunque a medida que los LLMs van aumentando de tamaño y van surgiendo nuevas capacidades, tenemos un problema y son las alucionaciones. Los autores del paper [DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models](https://arxiv.org/abs/2309.03883) proponen un método para evitar este problema.\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Proponen un enfoque de decodificación contrastiva, donde la probabilidad de salida de la siguiente palabra se obtiene de la diferencia en los logits entre una capa superior y una inferior. Al enfatizar el conocimiento de las capas superiores y restarle importancia al de las inferiores, podemos hacer que los LM sean más factuales y, por lo tanto, reducir las alucinaciones.\\n\",\n    \"\\n\",\n    \"En la siguiente figura se muestra esta idea. Mientras que `Seattle` mantiene una alta probabilidad en todas las capas, la probabilidad de la respuesta correcta `Olympia` aumenta después de que las capas superiores inyecten más conocimiento factual. Contrastar las diferencias entre las distintas capas puede revelar la respuesta correcta en este caso\\n\",\n    \"\\n\",\n    \"![DoLa-figure1](https://maximofn.com/wp-content/uploads/2024/07/DoLa-figure1.webp)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Método\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Un LLM consiste en una capa de embedding, varios transformers secuenciales y a continuación una capa de salida. Lo que proponen es medir la salida de cada transformer mediante la divergencia de Jensen-Shannon (JSD)\\n\",\n    \"\\n\",\n    \"En la siguiente figura se puede ver esta medida a la salida de cada transformer para una frase de entrada al LLM. Cada columna corresponde a un token de la frase\\n\",\n    \"\\n\",\n    \"![DoLa-figure2](https://maximofn.com/wp-content/uploads/2024/07/DoLa-figure2.webp)\\n\",\n    \"\\n\",\n    \"Se pueden observar dos patrones\\n\",\n    \"\\n\",\n    \" * El primero ocurre cuando se predicen entidades de nombre o fechas importantes, como `Wole Soyinka` y `1986`, que requieren conocimiento factual. Se puede ver que la JSD calculada sigue siendo extremadamente alta en las capas superiores. Este patrón indica que el modelo sigue cambiando sus predicciones en las últimas capas, y potencialmente inyectando más conocimiento factual en las predicciones\\n\",\n    \" \\n\",\n    \" * El segundo ocurre cuando se predicen palabras funcionales, como `was`, `the`, `to`, `in`, y los tokens copiados de la pregunta de entrada, como `first Nigerian`, `Nobel Prize`. Cuando se predicen estos tokens \\\"fáciles\\\", podemos observar que la JSD se vuelve muy pequeña a partir de las capas intermedias. Este hallazgo indica que el modelo ya ha decidido qué token generar en las capas intermedias, y mantiene las distribuciones de salida casi sin cambios en las capas superiores. Este hallazgo también es consistente con las suposiciones en los LLM de salida temprana `Schuster et al., 2022`\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Cuando la predicción de la siguiente palabra requiere conocimiento factual, el LLM parece cambiar las predicciones en las capas superiores. Contrastar las capas antes y después de un cambio repentino puede, por lo tanto, amplificar el conocimiento que emerge de las capas superiores y hacer que el modelo se base más en su conocimiento interno factual. Además, esta evolución de la información parece variar de un token a otro\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Su método requiere seleccionar con precisión la capa prematura que contiene información plausible pero menos factual, que puede no estar siempre en la misma capa temprana. Por lo tanto, proponen encontrar esa capa prematura mediante una selección dinámica de la capa prematura como se ve en la siguiente imagen\\n\",\n    \"\\n\",\n    \"![DoLa-figure3](https://maximofn.com/wp-content/uploads/2024/07/DoLa-figure3.webp)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Selección dinámica de la capa prematura\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Para seleccionar la capa prematura calculan la divergencia de Jensen-Shannon (JSD) entre las capas intermedias con la final. La capa prematura se selecciona como la capa con la JSD más alta\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Sin embargo, como este proceso puede ser un poco lento, lo que hacen es agrupar varias capas para hacer menos cálculos\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Contraste de las predicciones\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora que tenemos la última capa (capa madura) y la capa prematura, podemos contrastar las predicciones de ambas capas. Para ello, calculan la probabilidad logarítmica del siguiente token en la capa madura y la prematura. A continuación restan la probabilidad logarítmica de la capa prematura a la de la capa madura, así le dan más importancia al conocimiento de la capa madura\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Penalización por repetición\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"La motivación de DoLa es restar importancia al conocimiento lingüístico de las capas inferiores y amplificar el conocimiento factual del mundo real. Sin embargo, esto puede dar lugar a que el modelo genere párrafos gramaticalmente incorrectos\\n\",\n    \"\\n\",\n    \"Empíricamente no han observado ese problema, pero han encontrado que la distribución DoLa resultante a veces tiene una mayor tendencia a repetir frases generadas previamente, especialmente durante la generación de largas secuencias de razonamiento en la cadena de pensamiento\\n\",\n    \"\\n\",\n    \"Así que incluyen una penalización por repetición introducida en `Keskar et al. (2019)` con `θ = 1.2` durante la decodificación\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Implementación con transformers\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vamos a ver cómo implementar DoLa con la librería `transformers` de Hugging Face. Para obtener más información de cómo aplicar DoLa con la librer´ía `transformers` puedes consultar el siguiente [enlace](https://huggingface.co/docs/transformers/main/en/generation_strategies#dola-decoding)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Primero nos logeamos en el Hub, porque vamos a usar Llama 3 8B, para poder usarlo hay que pedir permiso a Meta, así que para poder descargarlo hay que estar logeado para que sepa que quién lo está descargando\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"from huggingface_hub import notebook_login\\n\",\n    \"notebook_login()\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora instanciamos el tokenizador y el modelo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed\\n\",\n    \"import torch\\n\",\n    \"\\n\",\n    \"compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16\\n\",\n    \"\\n\",\n    \"device = 'cuda' if torch.cuda.is_available() else 'cpu'\\n\",\n    \"checkpoints = \\\"meta-llama/Meta-Llama-3-8B-Instruct\\\"\\n\",\n    \"tokenizer = AutoTokenizer.from_pretrained(checkpoints)\\n\",\n    \"tokenizer.pad_token = tokenizer.eos_token\\n\",\n    \"model = AutoModelForCausalLM.from_pretrained(checkpoints, torch_dtype=compute_dtype, device_map=\\\"auto\\\")\\n\",\n    \"model.config.pad_token_id = model.config.eos_token_id\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Asignamos un valor fijo de semilla para la reproducibilidad del ejemplo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"set_seed(42)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Generamos los tokens de entrada al LLM\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"question = 'What does Darth Vader say to Luke in \\\"The Empire Strikes Back\\\"?'\\n\",\n    \"text = f\\\"Answer with a short answer.\\\\n\\\\nQuestion: {question}\\\\n\\\\nAnswer: \\\"\\n\",\n    \"inputs = tokenizer(text, return_tensors=\\\"pt\\\").to(model.device)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Generamos ahora la entrada vanilla, es decir, sin aplicar DoLa\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stderr\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.\\n\"\n     ]\n    },\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \" \\\"No, I am your father.\\\" (Note: This is a famous misquote. The actual quote is \\\"No, I am your father\\\" is not in the movie. The correct quote is \\\"No, I am your father.\\\" is not\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"generate_kwargs={\\n\",\n    \"    \\\"do_sample\\\": False,\\n\",\n    \"    \\\"max_new_tokens\\\": 50,\\n\",\n    \"    \\\"top_p\\\": None,\\n\",\n    \"    \\\"temperature\\\": None\\n\",\n    \"}\\n\",\n    \"\\n\",\n    \"vanilla_output = model.generate(**inputs, **generate_kwargs)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(vanilla_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vemos que sabe que hay un error famoso, pero no consigue decir la frase real\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora aplicando DoLa\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stderr\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.\\n\"\n     ]\n    },\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \" \\\"No, I am your father.\\\" (Note: This is one of the most famous lines in movie history, and it's often misquoted as \\\"Luke, I am your father.\\\")\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"dola_high_output = model.generate(**inputs, **generate_kwargs, dola_layers='high', repetition_penalty=1.2)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(dola_high_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora sí consigue dar la frase correcta y el [error famoso](https://www.bbc.co.uk/bitesize/articles/zc38kty)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vamos a hacer otra prueba con otro ejemplo, reinicio el notebook y uso otro modelo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed\\n\",\n    \"import torch\\n\",\n    \"\\n\",\n    \"compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16\\n\",\n    \"\\n\",\n    \"device = 'cuda' if torch.cuda.is_available() else 'cpu'\\n\",\n    \"checkpoints = \\\"huggyllama/llama-7b\\\"\\n\",\n    \"tokenizer = AutoTokenizer.from_pretrained(checkpoints)\\n\",\n    \"tokenizer.pad_token = tokenizer.eos_token\\n\",\n    \"model = AutoModelForCausalLM.from_pretrained(checkpoints, torch_dtype=compute_dtype, device_map=\\\"auto\\\")\\n\",\n    \"model.config.pad_token_id = model.config.eos_token_id\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Asignamos un valor fijo de semilla para la reproducibilidad del ejemplo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"set_seed(42)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Le escribo una nueva pregunta\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"text = \\\"On what date was the Declaration of Independence officially signed?\\\"\\n\",\n    \"inputs = tokenizer(text, return_tensors=\\\"pt\\\").to(device)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Generamos la salida vanilla\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"\\n\",\n      \"The Declaration of Independence was signed on July 4, 1776.\\n\",\n      \"What was the date of the signing of the Declaration of Independence?\\n\",\n      \"The Declaration of Independence was signed on July 4,\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"generate_kwargs={\\n\",\n    \"    \\\"do_sample\\\": False,\\n\",\n    \"    \\\"max_new_tokens\\\": 50,\\n\",\n    \"    \\\"top_p\\\": None,\\n\",\n    \"    \\\"temperature\\\": None\\n\",\n    \"}\\n\",\n    \"\\n\",\n    \"vanilla_output = model.generate(**inputs, **generate_kwargs)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(vanilla_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Como vemos genera mal la salida, ya que aunque se celebra el 4 de julio, en realidad fue firmada el [2 de julio](https://education.nationalgeographic.org/resource/signing-declaration-independence/)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vamos a probar ahora con DoLa\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"\\n\",\n      \"July 4, 1776. This is the most well-known date in U.S. history. The day has been celebrated with parades, barbeques, fireworks and festivals for hundreds of years.\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"dola_high_output = model.generate(**inputs, **generate_kwargs, dola_layers='high', repetition_penalty=1.2)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(dola_high_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Sigue sin generar una salida correcta, así que vamos a indicarle que solo contraste la capa final con las capas 28 y 30\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"\\n\",\n      \"It was officially signed on 2 August 1776, when 56 members of the Second Continental Congress put their John Hancocks to the Declaration. The 2-page document had been written in 17\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"dola_high_output = model.generate(**inputs, **generate_kwargs, dola_layers=[28,30], repetition_penalty=1.2)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(dola_high_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora sí consigue generar la respuesta correcta\"\n   ]\n  }\n ],\n \"metadata\": {\n  \"kernelspec\": {\n   \"display_name\": \"nlp_\",\n   \"language\": \"python\",\n   \"name\": \"python3\"\n  },\n  \"language_info\": {\n   \"codemirror_mode\": {\n    \"name\": \"ipython\",\n    \"version\": 3\n   },\n   \"file_extension\": \".py\",\n   \"mimetype\": \"text/x-python\",\n   \"name\": \"python\",\n   \"nbconvert_exporter\": \"python\",\n   \"pygments_lexer\": \"ipython3\",\n   \"version\": \"3.11.9\"\n  }\n },\n \"nbformat\": 4,\n \"nbformat_minor\": 2\n}\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```json\n{\n \"correccion0\": {\n  \"original\": \"Aunque a medida que los LLMs van aumentando de tamaño y van surgiendo nuevas capacidades, tenemos un problema y son las alucionaciones. Los autores del paper [DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models](https://arxiv.org/abs/2309.03883) proponen un método para evitar este problema.\",\n  \"correccion\": \"Aunque a medida que los LLMs van aumentando de tamaño y van surgiendo nuevas capacidades, tenemos un problema y son las alucinaciones. Los autores del paper [DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models](https://arxiv.org/abs/2309.03883) proponen un método para evitar este problema.\"\n },\n \"correccion1\": {\n  \"original\": \"Proponen un enfoque de decodificación contrastiva, donde la probabilidad de salida de la siguiente palabra se obtiene de la diferencia en los logits entre una capa superior y una inferior. Al enfatizar el conocimiento de las capas superiores y restarle importancia al de las inferiores, podemos hacer que los LM sean más factuales y, por lo tanto, reducir las alucinaciones.\\n\",\n  \"correccion\": \"Proponen un enfoque de decodificación contrastiva, donde la probabilidad de salida de la siguiente palabra se obtiene de la diferencia en los logits entre una capa superior y una inferior. Al enfatizar el conocimiento de las capas superiores y restarle importancia al de las inferiores, podemos hacer que los LM sean más factuales y, por lo tanto, reducir las alucinaciones.\\n\"\n },\n \"correccion2\": {\n  \"original\": \"Un LLM consiste en una capa de embedding, varios transformers secuenciales y a continuación una capa de salida. Lo que proponen es medir la salida de cada transformer mediante la divergencia de Jensen-Shannon (JSD)\\n\",\n  \"correccion\": \"Un LLM consiste en una capa de embedding, varios transformers secuenciales y a continuación una capa de salida. Lo que proponen es medir la salida de cada transformer mediante la divergencia de Jensen-Shannon (JSD)\\n\"\n },\n \"correccion3\": {\n  \"original\": \" * El primero ocurre cuando se predicen entidades de nombre o fechas importantes, como `Wole Soyinka` y `1986`, que requieren conocimiento factual. Se puede ver que la JSD calculada sigue siendo extremadamente alta en las capas superiores. Este patrón indica que el modelo sigue cambiando sus predicciones en las últimas capas, y potencialmente inyectando más conocimiento factual en las predicciones\\n\",\n  \"correccion\": \" * El primero ocurre cuando se predicen entidades de nombre o fechas importantes, como `Wole Soyinka` y `1986`, que requieren conocimiento factual. Se puede ver que la JSD calculada sigue siendo extremadamente alta en las capas superiores. Este patrón indica que el modelo sigue cambiando sus predicciones en las últimas capas y potencialmente inyectando más conocimiento factual en las predicciones\\n\"\n },\n \"correccion4\": {\n  \"original\": \"Su método requiere seleccionar con precisión la capa prematura que contiene información plausible pero menos factual, que puede no estar siempre en la misma capa temprana. Por lo tanto, proponen encontrar esa capa prematura mediante una selección dinámica de la capa prematura como se ve en la siguiente imagen\\n\",\n  \"correccion\": \"Su método requiere seleccionar con precisión la capa prematura que contiene información plausible pero menos factual, que puede no estar siempre en la misma capa temprana. Por lo tanto, proponen encontrar esa capa prematura mediante una selección dinámica de la capa prematura como se ve en la siguiente imagen\\n\"\n },\n \"correccion5\": {\n  \"original\": \"Para seleccionar la capa prematura calculan la divergencia de",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "{\n \"cells\": [\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"# DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Aunque a medida que los LLMs van aumentando de tamaño y van surgiendo nuevas capacidades, tenemos un problema y son las alucionaciones. Los autores del paper [DoLa: Decoding by Contrasting Layers Improves Factuality in Large Language Models](https://arxiv.org/abs/2309.03883) proponen un método para evitar este problema.\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Proponen un enfoque de decodificación contrastiva, donde la probabilidad de salida de la siguiente palabra se obtiene de la diferencia en los logits entre una capa superior y una inferior. Al enfatizar el conocimiento de las capas superiores y restarle importancia al de las inferiores, podemos hacer que los LM sean más factuales y, por lo tanto, reducir las alucinaciones.\\n\",\n    \"\\n\",\n    \"En la siguiente figura se muestra esta idea. Mientras que `Seattle` mantiene una alta probabilidad en todas las capas, la probabilidad de la respuesta correcta `Olympia` aumenta después de que las capas superiores inyecten más conocimiento factual. Contrastar las diferencias entre las distintas capas puede revelar la respuesta correcta en este caso\\n\",\n    \"\\n\",\n    \"![DoLa-figure1](https://maximofn.com/wp-content/uploads/2024/07/DoLa-figure1.webp)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Método\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Un LLM consiste en una capa de embedding, varios transformers secuenciales y a continuación una capa de salida. Lo que proponen es medir la salida de cada transformer mediante la divergencia de Jensen-Shannon (JSD)\\n\",\n    \"\\n\",\n    \"En la siguiente figura se puede ver esta medida a la salida de cada transformer para una frase de entrada al LLM. Cada columna corresponde a un token de la frase\\n\",\n    \"\\n\",\n    \"![DoLa-figure2](https://maximofn.com/wp-content/uploads/2024/07/DoLa-figure2.webp)\\n\",\n    \"\\n\",\n    \"Se pueden observar dos patrones\\n\",\n    \"\\n\",\n    \" * El primero ocurre cuando se predicen entidades de nombre o fechas importantes, como `Wole Soyinka` y `1986`, que requieren conocimiento factual. Se puede ver que la JSD calculada sigue siendo extremadamente alta en las capas superiores. Este patrón indica que el modelo sigue cambiando sus predicciones en las últimas capas, y potencialmente inyectando más conocimiento factual en las predicciones\\n\",\n    \" \\n\",\n    \" * El segundo ocurre cuando se predicen palabras funcionales, como `was`, `the`, `to`, `in`, y los tokens copiados de la pregunta de entrada, como `first Nigerian`, `Nobel Prize`. Cuando se predicen estos tokens \\\"fáciles\\\", podemos observar que la JSD se vuelve muy pequeña a partir de las capas intermedias. Este hallazgo indica que el modelo ya ha decidido qué token generar en las capas intermedias, y mantiene las distribuciones de salida casi sin cambios en las capas superiores. Este hallazgo también es consistente con las suposiciones en los LLM de salida temprana `Schuster et al., 2022`\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Cuando la predicción de la siguiente palabra requiere conocimiento factual, el LLM parece cambiar las predicciones en las capas superiores. Contrastar las capas antes y después de un cambio repentino puede, por lo tanto, amplificar el conocimiento que emerge de las capas superiores y hacer que el modelo se base más en su conocimiento interno factual. Además, esta evolución de la información parece variar de un token a otro\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Su método requiere seleccionar con precisión la capa prematura que contiene información plausible pero menos factual, que puede no estar siempre en la misma capa temprana. Por lo tanto, proponen encontrar esa capa prematura mediante una selección dinámica de la capa prematura como se ve en la siguiente imagen\\n\",\n    \"\\n\",\n    \"![DoLa-figure3](https://maximofn.com/wp-content/uploads/2024/07/DoLa-figure3.webp)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Selección dinámica de la capa prematura\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Para seleccionar la capa prematura calculan la divergencia de Jensen-Shannon (JSD) entre las capas intermedias con la final. La capa prematura se selecciona como la capa con la JSD más alta\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Sin embargo, como este proceso puede ser un poco lento, lo que hacen es agrupar varias capas para hacer menos cálculos\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Contraste de las predicciones\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora que tenemos la última capa (capa madura) y la capa prematura, podemos contrastar las predicciones de ambas capas. Para ello, calculan la probabilidad logarítmica del siguiente token en la capa madura y la prematura. A continuación restan la probabilidad logarítmica de la capa prematura a la de la capa madura, así le dan más importancia al conocimiento de la capa madura\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Penalización por repetición\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"La motivación de DoLa es restar importancia al conocimiento lingüístico de las capas inferiores y amplificar el conocimiento factual del mundo real. Sin embargo, esto puede dar lugar a que el modelo genere párrafos gramaticalmente incorrectos\\n\",\n    \"\\n\",\n    \"Empíricamente no han observado ese problema, pero han encontrado que la distribución DoLa resultante a veces tiene una mayor tendencia a repetir frases generadas previamente, especialmente durante la generación de largas secuencias de razonamiento en la cadena de pensamiento\\n\",\n    \"\\n\",\n    \"Así que incluyen una penalización por repetición introducida en `Keskar et al. (2019)` con `θ = 1.2` durante la decodificación\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"## Implementación con transformers\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vamos a ver cómo implementar DoLa con la librería `transformers` de Hugging Face. Para obtener más información de cómo aplicar DoLa con la librer´ía `transformers` puedes consultar el siguiente [enlace](https://huggingface.co/docs/transformers/main/en/generation_strategies#dola-decoding)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Primero nos logeamos en el Hub, porque vamos a usar Llama 3 8B, para poder usarlo hay que pedir permiso a Meta, así que para poder descargarlo hay que estar logeado para que sepa que quién lo está descargando\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"from huggingface_hub import notebook_login\\n\",\n    \"notebook_login()\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora instanciamos el tokenizador y el modelo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed\\n\",\n    \"import torch\\n\",\n    \"\\n\",\n    \"compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16\\n\",\n    \"\\n\",\n    \"device = 'cuda' if torch.cuda.is_available() else 'cpu'\\n\",\n    \"checkpoints = \\\"meta-llama/Meta-Llama-3-8B-Instruct\\\"\\n\",\n    \"tokenizer = AutoTokenizer.from_pretrained(checkpoints)\\n\",\n    \"tokenizer.pad_token = tokenizer.eos_token\\n\",\n    \"model = AutoModelForCausalLM.from_pretrained(checkpoints, torch_dtype=compute_dtype, device_map=\\\"auto\\\")\\n\",\n    \"model.config.pad_token_id = model.config.eos_token_id\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Asignamos un valor fijo de semilla para la reproducibilidad del ejemplo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"set_seed(42)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Generamos los tokens de entrada al LLM\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"question = 'What does Darth Vader say to Luke in \\\"The Empire Strikes Back\\\"?'\\n\",\n    \"text = f\\\"Answer with a short answer.\\\\n\\\\nQuestion: {question}\\\\n\\\\nAnswer: \\\"\\n\",\n    \"inputs = tokenizer(text, return_tensors=\\\"pt\\\").to(model.device)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Generamos ahora la entrada vanilla, es decir, sin aplicar DoLa\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stderr\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.\\n\"\n     ]\n    },\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \" \\\"No, I am your father.\\\" (Note: This is a famous misquote. The actual quote is \\\"No, I am your father\\\" is not in the movie. The correct quote is \\\"No, I am your father.\\\" is not\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"generate_kwargs={\\n\",\n    \"    \\\"do_sample\\\": False,\\n\",\n    \"    \\\"max_new_tokens\\\": 50,\\n\",\n    \"    \\\"top_p\\\": None,\\n\",\n    \"    \\\"temperature\\\": None\\n\",\n    \"}\\n\",\n    \"\\n\",\n    \"vanilla_output = model.generate(**inputs, **generate_kwargs)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(vanilla_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vemos que sabe que hay un error famoso, pero no consigue decir la frase real\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora aplicando DoLa\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stderr\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"Setting `pad_token_id` to `eos_token_id`:128001 for open-end generation.\\n\"\n     ]\n    },\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \" \\\"No, I am your father.\\\" (Note: This is one of the most famous lines in movie history, and it's often misquoted as \\\"Luke, I am your father.\\\")\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"dola_high_output = model.generate(**inputs, **generate_kwargs, dola_layers='high', repetition_penalty=1.2)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(dola_high_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora sí consigue dar la frase correcta y el [error famoso](https://www.bbc.co.uk/bitesize/articles/zc38kty)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vamos a hacer otra prueba con otro ejemplo, reinicio el notebook y uso otro modelo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed\\n\",\n    \"import torch\\n\",\n    \"\\n\",\n    \"compute_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16\\n\",\n    \"\\n\",\n    \"device = 'cuda' if torch.cuda.is_available() else 'cpu'\\n\",\n    \"checkpoints = \\\"huggyllama/llama-7b\\\"\\n\",\n    \"tokenizer = AutoTokenizer.from_pretrained(checkpoints)\\n\",\n    \"tokenizer.pad_token = tokenizer.eos_token\\n\",\n    \"model = AutoModelForCausalLM.from_pretrained(checkpoints, torch_dtype=compute_dtype, device_map=\\\"auto\\\")\\n\",\n    \"model.config.pad_token_id = model.config.eos_token_id\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Asignamos un valor fijo de semilla para la reproducibilidad del ejemplo\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"set_seed(42)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Le escribo una nueva pregunta\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [],\n   \"source\": [\n    \"text = \\\"On what date was the Declaration of Independence officially signed?\\\"\\n\",\n    \"inputs = tokenizer(text, return_tensors=\\\"pt\\\").to(device)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Generamos la salida vanilla\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"\\n\",\n      \"The Declaration of Independence was signed on July 4, 1776.\\n\",\n      \"What was the date of the signing of the Declaration of Independence?\\n\",\n      \"The Declaration of Independence was signed on July 4,\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"generate_kwargs={\\n\",\n    \"    \\\"do_sample\\\": False,\\n\",\n    \"    \\\"max_new_tokens\\\": 50,\\n\",\n    \"    \\\"top_p\\\": None,\\n\",\n    \"    \\\"temperature\\\": None\\n\",\n    \"}\\n\",\n    \"\\n\",\n    \"vanilla_output = model.generate(**inputs, **generate_kwargs)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(vanilla_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Como vemos genera mal la salida, ya que aunque se celebra el 4 de julio, en realidad fue firmada el [2 de julio](https://education.nationalgeographic.org/resource/signing-declaration-independence/)\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Vamos a probar ahora con DoLa\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"\\n\",\n      \"July 4, 1776. This is the most well-known date in U.S. history. The day has been celebrated with parades, barbeques, fireworks and festivals for hundreds of years.\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"dola_high_output = model.generate(**inputs, **generate_kwargs, dola_layers='high', repetition_penalty=1.2)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(dola_high_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Sigue sin generar una salida correcta, así que vamos a indicarle que solo contraste la capa final con las capas 28 y 30\"\n   ]\n  },\n  {\n   \"cell_type\": \"code\",\n   \"execution_count\": null,\n   \"metadata\": {},\n   \"outputs\": [\n    {\n     \"name\": \"stdout\",\n     \"output_type\": \"stream\",\n     \"text\": [\n      \"\\n\",\n      \"It was officially signed on 2 August 1776, when 56 members of the Second Continental Congress put their John Hancocks to the Declaration. The 2-page document had been written in 17\\n\"\n     ]\n    }\n   ],\n   \"source\": [\n    \"dola_high_output = model.generate(**inputs, **generate_kwargs, dola_layers=[28,30], repetition_penalty=1.2)\\n\",\n    \"\\n\",\n    \"print(tokenizer.batch_decode(dola_high_output[:, inputs.input_ids.shape[-1]:], skip_special_tokens=True)[0])\"\n   ]\n  },\n  {\n   \"cell_type\": \"markdown\",\n   \"metadata\": {},\n   \"source\": [\n    \"Ahora sí consigue generar la respuesta correcta\"\n   ]\n  }\n ],\n \"metadata\": {\n  \"kernelspec\": {\n   \"display_name\": \"nlp_\",\n   \"language\": \"python\",\n   \"name\": \"python3\"\n  },\n  \"language_info\": {\n   \"codemirror_mode\": {\n    \"name\": \"ipython\",\n    \"version\": 3\n   },\n   \"file_extension\": \".py\",\n   \"mimetype\": \"text/x-python\",\n   \"name\": \"python\",\n   \"nbconvert_exporter\": \"python\",\n   \"pygments_lexer\": \"ipython3\",\n   \"version\": \"3.11.9\"\n  }\n },\n \"nbformat\": 4,\n \"nbformat_minor\": 2\n}\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "```json\n{\n \"correccion0\": {\n  \"original\": \"Vamos a ver cómo implementar DoLa con la librería `transformers` de Hugging Face. Para obtener más información de cómo aplicar DoLa con la librer´ía `transformers` puedes consultar el siguiente [enlace](https://huggingface.co/docs/transformers/main/en/generation_strategies#dola-decoding)\",\n  \"correccion\": \"Vamos a ver cómo implementar DoLa con la librería `transformers` de Hugging Face. Para obtener más información de cómo aplicar DoLa con la librería `transformers` puedes consultar el siguiente [enlace](https://huggingface.co/docs/transformers/main/en/generation_strategies#dola-decoding)\",\n  \"explicación\": \"Se ha corregido la palabra \\\"librer´ía\\\" por \\\"librería\\\".\"\n },\n \"correccion1\": {\n  \"original\": \"Primero nos logeamos en el Hub, porque vamos a usar Llama 3 8B, para poder usarlo hay que pedir permiso a Meta, así que para poder descargarlo hay que estar logeado para que sepa que quién lo está descargando\",\n  \"correccion\": \"Primero nos logeamos en el Hub, porque vamos a usar Llama 3 8B, para poder usarlo hay que pedir permiso a Meta, así que para poder descargarlo hay que estar logueado para que sepa quién lo está descargando.\",\n  \"explicación\": \"Se ha corregido la palabra \\\"logeado\\\" por \\\"logueado\\\" para mantener la concordancia.\"\n }\n}\n```",
                ],
            },
        ]
    )

    return chat_session

def chat_with_gemini(chat_session, input_text):
    # response = chat_session.send_message(input_text)
    try:
        response = chat_session.send_message(input_text)
    except Exception as e:
        print(f'Error: {e}')
        if str(QUOTA_EXCEEDED_ERROR) in str(e):
            print('Quota exceeded')
            response = QUOTA_EXCEEDED_ERROR
        else:
            response = None
    return response

def get_notebook_content(notebook_path):
    with open(notebook_path, 'r') as file:
        return file.read()

def notebook_string_content_to_dict(notebook_content):
    filter_text = notebook_content.replace('```json', '').replace('\n', '').replace('```', '')
    notebook_content_json = json.loads(filter_text)
    notebook_content_dict = dict(notebook_content_json)

def get_path_name_and_extension(path):
    # return path, name and extension of a file
    path_name, extension = os.path.splitext(path)
    file_name = path_name.split('/')[-1]
    path = path_name.replace(file_name, '')
    return path, file_name, extension

def save_corrections_dict(file_name, corrections_dict):
    portfolio_path = get_portafolio_path(os.getcwd())

    json_path = os.path.join(portfolio_path, 'preparar_notebook/corrections', f'{file_name}.json')

    with open(json_path, 'w') as file:
        json.dump(corrections_dict, file)

def create_corrections_dict(notebook_path):
    load_gemini_api_key()
    chat_session = create_model()

    notebook_content = get_notebook_content(notebook_path)

    gemini_corrections = chat_with_gemini(chat_session, notebook_content)
    if not gemini_corrections:
        return None
    elif gemini_corrections == QUOTA_EXCEEDED_ERROR:
        return QUOTA_EXCEEDED_ERROR
    gemini_correctios_dict = notebook_string_content_to_dict(gemini_corrections)

    # gemini_correctios_dict = {
    #     "correccion0": {
    #         "original": "Para escribir un `string` muy largo y no tener una fila que ocupe mucho espacio se puede introducir en varias lineas",
    #         "correccion": "Para escribir un `string` muy largo y no tener una fila que ocupe mucho espacio se puede introducir en varias líneas",
    #         "explicación": "Se ha corregido \"lineas\" por \"líneas\"."
    #     },
    #     "correccion1": {
    #         "original": "Sin embargo vemos que en medio ha metido el caracter `\\n`, este caracter indica el salto de linea. Si usamos la función `print()` veremos como ya no aparece",
    #         "correccion": "Sin embargo vemos que en medio ha metido el carácter `\\n`, este carácter indica el salto de línea. Si usamos la función `print()` veremos como ya no    aparece",
    #         "explicación": "Se ha corregido \"caracter\" por \"carácter\" (dos veces) y \"linea\" por \"línea\"."
    #     },
    #     "correccion2": {
    #         "original": "Como hemos dicho los strings son cadenas de caracteres, por lo que podemos navegar e iterar a traves de ellos",
    #         "correccion": "Como hemos dicho los strings son cadenas de caracteres, por lo que podemos navegar e iterar a través de ellos",
    #         "explicación": "Se ha corregido \"a traves\" por \"a través\"."
    #     },
    #     "correccion3": {
    #         "original": "Antes explicamos que el caracter `\\n` correspondía a una salto de linea, este caracter especial corresponde a una serie de caracteres especiales llamados     `Escape Characters`. Veamos otros",
    #         "correccion": "Antes explicamos que el carácter `\\n` correspondía a un salto de línea, este carácter especial corresponde a una serie de caracteres especiales llamados    `Escape Characters`. Veamos otros",
    #         "explicación": "Se ha corregido \"caracter\" por \"carácter\" (dos veces), \"una salto\" por \"un salto\" y \"linea\" por \"línea\"."
    #     },
    # }

    notebook_path, notebook_name, notebook_extension = get_path_name_and_extension(notebook_path)

    save_corrections_dict(notebook_name, gemini_correctios_dict)

    return gemini_correctios_dict

def codification_characters_to_ansi(text):
    # ANSI UTF-8	JAVASCRIPT	HTML
    # Â	   u00a0	&#160;
    # ¡	   Â¡	u00a1	&#161;
    # ¢	   Â¢	u00a2	&#162;
    # £	   Â£	u00a3	&#163;
    # ¤	   Â¤	u00a4	&#164;
    # ¥	   Â¥	u00a5	&#165;
    # ¦	   Â¦	u00a6	&#166;
    # §	   Â§	u00a7	&#167;
    # ¨	   Â¨	u00a8	&#168;
    # ©	   Â©	u00a9	&#169;
    # ª	   Âª	u00aa	&#170;
    # «	   Â«	u00ab	&#171;
    # ¬	   Â¬	u00ac	&#172;
    # ­	    Â­	  u00ad	&#173;
    # ®	   Â®	u00ae	&#174;
    # ¯	   Â¯	u00af	&#175;
    # °	   Â°	u00b0	&#176;
    # ±	   Â±	u00b1	&#177;
    # ²	   Â²	u00b2	&#178;
    # ³	   Â³	u00b3	&#179;
    # ´	   Â´	u00b4	&#180;
    # µ	   Âµ	u00b5	&#181;
    # ¶	   Â¶	u00b6	&#182;
    # ·	   Â·	u00b7	&#183;
    # ¸	   Â¸	u00b8	&#184;
    # ¹	   Â¹	u00b9	&#185;
    # º	   Âº	u00ba	&#186;
    # »	   Â»	u00bb	&#187;
    # ¼	   Â¼	u00bc	&#188;
    # ½	   Â½	u00bd	&#189;
    # ¾	   Â¾	u00be	&#190;
    # ¿	   Â¿	u00bf	&#191;
    # À	   Ã€	u00c0	&#192;
    # Á	   Ã	u00c1	&#193;
    # Â	   Ã‚	u00c2	&#194;
    # Ã	   Ãƒ	u00c3	&#195;
    # Ä	   Ã„	u00c4	&#196;
    # Å	   Ã…	u00c5	&#197;
    # Æ	   Ã†	u00c6	&#198;
    # Ç	   Ã‡	u00c7	&#199;
    # È	   Ãˆ	u00c8	&#200;
    # É	   Ã‰	u00c9	&#201;
    # Ê	   ÃŠ	u00ca	&#202;
    # Ë	   Ã‹	u00cb	&#203;
    # Ì	   ÃŒ	u00cc	&#204;
    # Í	   Ã	u00cd	&#205;
    # Î	   ÃŽ	u00ce	&#206;
    # Ï	   Ã	u00cf	&#207;
    # Ð	   Ã	u00d0	&#208;
    # Ñ	   Ã‘	u00d1	&#209;
    # Ò	   Ã’	u00d2	&#210;
    # Ó	   Ã“	u00d3	&#211;
    # Ô	   Ã”	u00d4	&#212;
    # Õ	   Ã•	u00d5	&#213;
    # Ö	   Ã–	u00d6	&#214;
    # ×	   Ã—	u00d7	&#215;
    # Ø	   Ã˜	u00d8	&#216;
    # Ù	   Ã™	u00d9	&#217;
    # Ú	   Ãš	u00da	&#218;
    # Û	   Ã›	u00db	&#219;
    # Ü	   Ãœ	u00dc	&#220;
    # Ý	   Ã	u00dd	&#221;
    # Þ	   Ãž	u00de	&#222;
    # ß	   ÃŸ	u00df	&#223;
    # à	   Ã	u00e0	&#224;
    # á	   Ã¡	u00e1	&#225;
    # â	   Ã¢	u00e2	&#226;
    # ã	   Ã£	u00e3	&#227;
    # ä	   Ã¤	u00e4	&#228;
    # å	   Ã¥	u00e5	&#229;
    # æ	   Ã¦	u00e6	&#230;
    # ç	   Ã§	u00e7	&#231;
    # è	   Ã¨	u00e8	&#232;
    # é	   Ã©	u00e9	&#233;
    # ê	   Ãª	u00ea	&#234;
    # ë	   Ã«	u00eb	&#235;
    # ì	   Ã¬	u00ec	&#236;
    # í	   Ã­	u00ed	&#237;
    # î	   Ã®	u00ee	&#238;
    # ï	   Ã¯	u00ef	&#239;
    # ð	   Ã°	u00f0	&#240;
    # ñ	   Ã±	u00f1	&#241;
    # ò	   Ã²	u00f2	&#242;
    # ó	   Ã³	u00f3	&#243;
    # ô	   Ã´	u00f4	&#244;
    # õ	   Ãµ	u00f5	&#245;
    # ö	   Ã¶	u00f6	&#246;
    # ÷	   Ã·	u00f7	&#247;
    # ø	   Ã¸	u00f8	&#248;
    # ù	   Ã¹	u00f9	&#249;
    # ú	   Ãº	u00fa	&#250;
    # û	   Ã»	u00fb	&#251;
    # ü	   Ã¼	u00fc	&#252;
    # ý	   Ã½	u00fd	&#253;
    # þ	   Ã¾	u00fe	&#254;
    # ÿ	   Ã¿	u00ff	&#255;
    return text.replace('\u00a0', '').replace('\u00a1', '¡').replace('\u00a2', '¢').replace('\u00a3', '£').replace('\u00a4', '¤').replace('\u00a5', '¥').replace('\u00a6', '¦').replace('\u00a7', '§').replace('\u00a8', '¨').replace('\u00a9', '©').replace('\u00aa', 'ª').replace('\u00ab', '«').replace('\u00ac', '¬').replace('\u00ad', '­').replace('\u00ae', '®').replace('\u00af', '¯').replace('\u00b0', '°').replace('\u00b1', '±').replace('\u00b2', '²').replace('\u00b3', '³').replace('\u00b4', '´').replace('\u00b5', 'µ').replace('\u00b6', '¶').replace('\u00b7', '·').replace('\u00b8', '¸').replace('\u00b9', '¹').replace('\u00ba', 'º').replace('\u00bb', '»').replace('\u00bc', '¼').replace('\u00bd', '½').replace('\u00be', '¾').replace('\u00bf', '¿').replace('\u00c0', 'À').replace('\u00c1', 'Á').replace('\u00c2', 'Â').replace('\u00c3', 'Ã').replace('\u00c4', 'Ä').replace('\u00c5', 'Å').replace('\u00c6', 'Æ').replace('\u00c7', 'Ç').replace('\u00c8', 'È').replace('\u00c9', 'É').replace('\u00ca', 'Ê').replace('\u00cb', 'Ë').replace('\u00cc', 'Ì').replace('\u00cd', 'Í').replace('\u00ce', 'Î').replace('\u00cf', 'Ï').replace('\u00d0', 'Ð').replace('\u00d1', 'Ñ').replace('\u00d2', 'Ò').replace('\u00d3', 'Ó').replace('\u00d4', 'Ô').replace('\u00d5', 'Õ').replace('\u00d6', 'Ö').replace('\u00d7', '×').replace('\u00d8', 'Ø').replace('\u00d9', 'Ù').replace('\u00da', 'Ú').replace('\u00db', 'Û').replace('\u00dc', 'Ü').replace('\u00dd', 'Ý').replace('\u00de', 'Þ').replace('\u00df', 'ß').replace('\u00e0', 'à').replace('\u00e1', 'á').replace('\u00e2', 'â').replace('\u00e3', 'ã').replace('\u00e4', 'ä').replace('\u00e5', 'å').replace('\u00e6', 'æ').replace('\u00e7', 'ç').replace('\u00e8', 'è').replace('\u00e9', 'é').replace('\u00ea', 'ê').replace('\u00eb', 'ë').replace('\u00ec', 'ì').replace('\u00ed', 'í').replace('\u00ee', 'î').replace('\u00ef', 'ï').replace('\u00f0', 'ð').replace('\u00f1', 'ñ').replace('\u00f2', 'ò').replace('\u00f3', 'ó').replace('\u00f4', 'ô').replace('\u00f5', 'õ').replace('\u00f6', 'ö').replace('\u00f7', '÷').replace('\u00f8', 'ø').replace('\u00f9', 'ù').replace('\u00fa', 'ú').replace('\u00fb', 'û').replace('\u00fc', 'ü').replace('\u00fd', 'ý').replace('\u00fe', 'þ').replace('\u00ff', 'ÿ')

def get_similarity_between_strings(string1, string2):
    embedding1 = torch.from_numpy(encoder_model.encode(string1))
    embedding2 = torch.from_numpy(encoder_model.encode(string2))

    similarity = cosine_similarity(embedding1.unsqueeze(0), embedding2.unsqueeze(0))
    return similarity.item()

def apply_corrections(notebook_path, corrections_dict):
    # Get notebook content and convert it to a dictionary
    with open(notebook_path, 'r') as file:
        notebook_content = file.read()
    notebook_content_dict = json.loads(notebook_content)
    
    # Apply corrections
    total_number_corrections = len(corrections_dict)
    for i, correction in enumerate(corrections_dict):
        original_text = corrections_dict[correction]['original']
        corrected_text = corrections_dict[correction]['correccion']
        explain_text = corrections_dict[correction]['explicación']

        original_text_founded = False
        for cell in notebook_content_dict['cells']: # Iterate over cells
            for j in range(len(cell['source'])):    # Iterate over cell sources, all the text in a cell
                similarity = get_similarity_between_strings(original_text, cell['source'][j])
                if similarity > SIMILARITY_THRESHOLD:
                    original_text_founded = True
                    print(f"\nCorrection {i} of {total_number_corrections}: {explain_text}")
                    # print(f"\tOriginal : {original_text}")
                    print(f"\tOriginal : {cell['source'][j]}")
                    print(f"\tCorrected: {corrected_text}")
                    print("Do you want to apply this correction? (y/n)", end=' ')
                    answer = input()
                    while answer.lower() not in ['y', 'n', 'yes', 'no']:
                        print("Please, write 'y' or 'n'", end=' ')
                        answer = input()
                    if answer.lower() in ['y', 'yes']:
                        cell['source'][j] = cell['source'][j].replace(original_text, corrected_text)
                        print("Correction applied")
                    else:
                        print("Correction not applied")
                    break   # Break the loop over cell sources, all the text in a cell
            if original_text_founded:
                break   # Break the loop over cells
        
        # If the original text is not found, print the correction and ask the user to apply it manually
        if not original_text_founded:
            print(f"\nCorrection {i} not found: {explain_text}")
            print(f"\tOriginal : {original_text}")
            print(f"\tCorrected: {corrected_text}")
            print("Change it manually. Done? type 'done' or 'd' to continue", end=' ')
            answer = input()
            while answer.lower() not in ['done', 'd']:
                print("Please, write 'done' or 'd'", end=' ')
                answer = input()
            if answer.lower() in ['done', 'd']:
                print("Correction applied manually")

    # Save the corrected notebook
    with open(notebook_path, 'w') as file:
        json.dump(notebook_content_dict, file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocess a Jupyter notebook')
    parser.add_argument('notebook_path', type=str, help='Path to the notebook')
    args = parser.parse_args()
    notebook_path = args.notebook_path

    gemini_correctios_dict = create_corrections_dict(notebook_path)
    print(gemini_correctios_dict)