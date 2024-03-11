from openai import OpenAI
import openai
import storage
import random
import json


with open("secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]


client = OpenAI(api_key=openai_key)


def openai_complete(model, messages):
    print(messages)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content



