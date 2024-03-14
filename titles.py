from openai import OpenAI
import json

with open("test_mode.json", "r") as file:
    test_mode = json.load(file)["test_mode"]


with open("secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]


client = OpenAI(api_key=openai_key)


def make_title(user_message, ai_response, model):

    if test_mode:
        return " ".join(user_message.split()[:3])

    messages = [{
        "role": "user",
        "content": f"""
        "User: {user_message}\nAI: {ai_response}"
        
        "Make a short title, no more than a few words, for this conversation, in the language of the message."
        """
    }]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    # Retrieve the full text from the completion without streaming
    text = completion.choices[0].message.content

    return text