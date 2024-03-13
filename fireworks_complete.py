import json
from fireworks.client import Fireworks

def load_api_key():
    with open("secrets.json", "r") as file:
        secrets = json.load(file)
    return secrets["fireworks"]

client = Fireworks(api_key=load_api_key())

def fireworks_complete(model, messages):
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content