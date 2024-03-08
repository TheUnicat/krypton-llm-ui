import openai

"Make a short title, no more than a few words, for this conversation, in the language of the message."


def openai_complete(messages):
    messages = {
        "role"
    }
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )

    for chunk in completion:
        yield chunk.choices[0].delta.content