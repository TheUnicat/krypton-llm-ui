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


def format_messages(conversations, new_images=[]):
    has_images = False
    """
    Converts a list of conversations in OpenAI format to Google format, including images.
    New images to be added to the final message if present.
    """
    google_format_conversations = []
    for conversation in conversations:
        parts = [conversation['content']] if 'content' in conversation else []
        # Check for and convert image data to PIL Image objects, then add to parts
        if 'image_data' in conversation:
            for image_data in conversation['image_data']:
                has_images = True
                parts.append(base64_to_image(image_data['base64']))
        google_format_conversations.append({
            'role': "user" if conversation['role'] == "user" else "model",
            'parts': parts
        })

    # Add new images to the final message if any
    if new_images:
        has_images = True
        if not google_format_conversations:
            google_format_conversations.append({'role': 'user', 'parts': []})
        last_message_parts = google_format_conversations[-1]['parts']
        for image_data in new_images:
            last_message_parts.append(base64_to_image(image_data['image']))

    return google_format_conversations, has_images


def google_complete(model, messages, images=[], max_tokens=4096, system_prompt=None, tools=[]):
    model_name = model_utils.get_model(model)

    messages, has_images = format_messages(messages, images)
    if has_images:
        model_name = "gemini-pro-vision"

    final_model_object = genai.GenerativeModel(model_name)

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