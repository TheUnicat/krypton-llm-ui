from openai import OpenAI
import json
import utils

with open("secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]

client = OpenAI(api_key=openai_key)


def openai_complete(model, messages):


    model_name = utils.get_model(model[0], model[1])
    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        stream=True
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content
