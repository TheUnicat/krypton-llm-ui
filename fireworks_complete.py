import json
from fireworks.client import Fireworks
import utils

def load_api_key():
    with open("secrets.json", "r") as file:
        secrets = json.load(file)
    return secrets["fireworks"]

client = Fireworks(api_key=load_api_key())

def fireworks_complete(model, messages, max_tokens=4096):
    model_name = utils.get_model_path(model[0], model[1])
    print(model_name)
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True,
        max_tokens=max_tokens
    )

    for chunk in completion:
        print(chunk)
        try:
            yield chunk[1][0].message.content
        except Exception as e:
            print(e)
