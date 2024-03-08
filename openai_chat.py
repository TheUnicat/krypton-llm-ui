from openai import OpenAI
import openai
import storage
import random
import json

openai_key = json.load("secrets.json")["openai"]


client = OpenAI(api_key=openai_key)


def openai_complete(model, prompt, conversation_id):


    messages = storage.format_conversation(storage.retrieve_conversation(conversation_id)["conversation"])

    print(messages)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content

def openai_test(model, prompt, conversation_id):

    lorem_ipsum_words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
        "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
        "incididunt", "ut", "labore", "et", "dolore", "magna",
        "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis",
        "nostrud", "exercitation", "ullamco", "laboris", "nisi",
        "ut", "aliquip", "ex", "ea", "commodo", "consequat"
    ]

    # Randomly select 20 words from the lorem_ipsum_words list
    random_words = random.sample(lorem_ipsum_words, 20)

    # Join the selected words into a single string
    random_lorem_ipsum = ' '.join(random_words)

    # Yield the generated string
    yield random_lorem_ipsum


