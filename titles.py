from openai import OpenAI
import json


with open("secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]


client = OpenAI(api_key=openai_key)


def make_title(user_message, ai_response):
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