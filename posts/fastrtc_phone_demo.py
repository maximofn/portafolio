from fastrtc import ReplyOnPause, Stream, get_stt_model, get_tts_model
import gradio
from gradio_client import Client
import os
from gradio.networking import setup_tunnel as original_setup_tunnel
import socket

# Monkey patch setup_tunnel para que acepte el parámetro adicional
def patched_setup_tunnel(host, port, share_token, share_server_address, share_server_tls_certificate=None):
    return original_setup_tunnel(host, port, share_token, share_server_address, share_server_tls_certificate)

# Replace the original function with our patched version
gradio.networking.setup_tunnel = patched_setup_tunnel

# Get the token from the environment variable
HUGGINGFACE_FASTRTC_PHONE_CALL_TOKEN = os.getenv("HUGGINGFACE_FASTRTC_PHONE_CALL_TOKEN")

# Initialize the LLM client
llm_client = Client("Maximofn/SmolLM2_localModel")

# Initialize the STT and TTS models
stt_model = get_stt_model()
tts_model = get_tts_model()

# Define the echo function
def echo(audio):
    # Convert the audio to text
    prompt = stt_model.stt(audio)

    # Generate the response
    response = llm_client.predict(
            message=prompt,
            system_message="You are a friendly Chatbot. Always reply in the language in which the user is writing to you.",
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            api_name="/chat"
    )
    
    # Convert the response to audio
    prompt = response

    # Stream the audio
    for audio_chunk in tts_model.stream_tts_sync(prompt):
        yield audio_chunk

def find_free_port(start_port=8000, max_port=9000):
    """Find the first free port starting from start_port."""
    print(f"Searching for a free port starting from {start_port}...")
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('127.0.0.1', port))
            if result != 0:  # If result != 0, the port is free
                print(f"Free port found: {port}")
                return port
    raise RuntimeError(f"No free port found between {start_port} and {max_port}")

stream = Stream(ReplyOnPause(echo), modality="audio", mode="send-receive")
free_port = find_free_port()    # Search for a free port
stream.fastphone(token=HUGGINGFACE_FASTRTC_PHONE_CALL_TOKEN, port=free_port)