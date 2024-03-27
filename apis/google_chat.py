import json
import base64
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from utils import model_utils


with open("krypton_storage/secrets.json", "r") as file:
    google_key = json.load(file)["google"]

genai.configure(api_key=google_key)


def base64_to_image(base64_string):
    # Decode the Base64 string
    image_data = base64.b64decode(base64_string)
    # Convert binary data to image data with BytesIO, which PIL can open
    image = Image.open(BytesIO(image_data))
    return image
def convert_openai_to_google_messages(conversations):
    """
    Converts a list of conversations in OpenAI format to Google format.

    OpenAI format: [{'role': 'user', 'content': 'hello'}]
    Google format: [{'role': 'user', 'parts': ['hello']}]
    """
    google_format_conversations = []
    for conversation in conversations:
        google_format_conversations.append({
            'role': "user" if conversation['role'] == "user" else "model",
            'parts': [conversation['content']]
        })
    return google_format_conversations


def google_complete(model, messages, images=[], max_tokens=4096, system_prompt=None):
    model_name = model_utils.get_model(model)
    final_model_object = genai.GenerativeModel(model_name)

    messages = convert_openai_to_google_messages(messages)
    response = final_model_object.generate_content(messages,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
    },
    stream=True)

    for chunk in response:
        yield chunk.text