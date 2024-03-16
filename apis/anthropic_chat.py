import json
import anthropic
from utils import model_utils

with open("krypton_storage/secrets.json", "r") as file:
    anthropic_key = json.load(file)["anthropic"]

client = anthropic.Anthropic(
    api_key=anthropic_key,
)

def anthropic_complete(model, messages, max_tokens=4096):
    model_name = model_utils.get_model(model)
    print(model)
    with client.messages.stream(
            max_tokens=max_tokens,
            messages=messages,
            model=model_name,
    ) as stream:
        for text in stream.text_stream:
            yield text
    #
    # for chunk in completion:
    #     yield chunk.choices[0].delta.content