import json
import anthropic
from utils import model_utils
from typing import Dict, List

with open("krypton_storage/secrets.json", "r") as file:
    anthropic_key = json.load(file)["anthropic"]

client = anthropic.Anthropic(
    api_key=anthropic_key
)

def format_tools(schemas: List[Dict]) -> List[Dict]:
    converted_schemas = []

    for schema in schemas:
        if schema["type"] == "function":
            function_schema = schema["function"]
            converted_schema = {
                "name": function_schema["name"],
                "description": function_schema["description"],
                "input_schema": function_schema["parameters"]
            }
            converted_schemas.append(converted_schema)

    return converted_schemas


def anthropic_complete(model, messages, images=[], max_tokens=4096, system_prompt=None, tools=[]):
    model_name = model_utils.get_model(model)

    # Reformat messages to include image data if present
    updated_messages = []
    for message in messages[:-1]:
        if message.get("image_data") and len(message["image_data"]) > 0:
            new_content = [{"type": "text", "text": message["content"]}]
            for image_data in message["image_data"]:
                new_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_data["mime"],
                        "data": image_data["base64"]
                    }
                })
            updated_messages.append({"role": message["role"], "content": new_content})
        else:
            updated_messages.append(message)

    updated_messages.append(messages[-1])

    # Check if the images list is not empty
    if images:
        # Reformat the last message in the updated_messages list to include image data
        last_message = updated_messages[-1]
        new_content = [{"type": "text", "text": last_message["content"]}]
        for image_data in images:
            new_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_data["type"],
                    "data": image_data["image"]
                }
            })
        updated_messages[-1] = {"role": "user", "content": new_content}

    # Continue with your existing logic for streaming messages
    if system_prompt is not None:
        with client.messages.stream(
            max_tokens=max_tokens,
            messages=updated_messages,
            model=model_name,
            system=system_prompt
        ) as stream:
            for text in stream.text_stream:
                yield text
    else:
        with client.messages.stream(
            max_tokens=max_tokens,
            messages=updated_messages,
            model=model_name
        ) as stream:
            for text in stream.text_stream:
                yield text