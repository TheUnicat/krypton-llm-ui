from openai import OpenAI
import json
from utils import model_utils

with open("krypton_storage/secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]

client = OpenAI(api_key=openai_key)


def openai_complete(model, messages, max_tokens=4096):

    model_name = model_utils.get_model(model[0], model[1])
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True,
        max_tokens=max_tokens
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content
