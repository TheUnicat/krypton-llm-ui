import json
import anthropic
from utils import model_utils

with open("krypton_storage/secrets.json", "r") as file:
    anthropic_key = json.load(file)["anthropic"]

client = anthropic.Anthropic(
    api_key=anthropic_key,
)


def anthropic_complete(model, messages, images=[], max_tokens=4096):
    model_name = model_utils.get_model(model)
    print(model)

    # Check if the images list is not empty
    if images:
        # Reformat the last message in the messages list to include image data
        last_message = messages[-1]
        new_content = [{
            "type": "text",
            "text": last_message["content"]
        }] + [{
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_data["type"],  # Use the MIME type from the loaded image data
                "data": image_data["image"]  # Use the Base64-encoded image data
            }
        } for image_data in images]

        # Update the last message to include both text and images
        messages[-1] = {
            "role": "user",
            "content": new_content
        }

    # Continue with your existing logic for streaming messages
    with client.messages.stream(
            max_tokens=max_tokens,
            messages=messages,
            model=model_name,
    ) as stream:
        for text in stream.text_stream:
            yield text

