from openai import OpenAI
import json
from utils import model_utils

with open("krypton_storage/secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]

client = OpenAI(api_key=openai_key)


def openai_complete(model, messages, images=[], max_tokens=4096, system_prompt=None):
    model_name = model_utils.get_model(model)

    # Reformat messages to include image data if present
    updated_messages = []
    for message in messages[:-1]:
        if message.get("image_data") and len(message["image_data"]) > 0:
            new_content = [{"type": "text", "text": message["content"]}]
            for image_data in message["image_data"]:
                # Format the image data as a URL with base64 string
                base64_image = image_data["base64"]
                image_url = f"data:{image_data['mime']};base64,{base64_image}"
                new_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })
            updated_messages.append({"role": message["role"], "content": new_content})
        else:
            updated_messages.append(message)

    updated_messages.append(messages[-1])

    # Check if the images list is not empty and reformat accordingly
    if images:
        # Reformat the last message in the updated_messages list to include image URLs
        last_message = updated_messages[-1]
        new_content = [{"type": "text", "text": last_message["content"]}]
        for image_data in images:
            # Format the image data as a URL with base64 string
            base64_image = image_data["image"]
            image_url = f"data:{image_data['type']};base64,{base64_image}"
            new_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })
        updated_messages[-1] = {"role": "user", "content": new_content}

    if system_prompt:
        updated_messages.insert(0, {
            "role": "system",
            "content": system_prompt
        }
        )

    completion = client.chat.completions.create(
        model=model_name,
        messages=updated_messages,
        stream=True,
        max_tokens=max_tokens
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content
