import storage
from openai_chat import openai_complete
import json
from test import test_complete
#from eagle_chat import eagle_complete


TEST = True

with open("models.json", "r") as file:
    models = json.load(file)

def format_to_chat(model, prompt, conversation_id, message_id):

    if TEST:
        model = "test"


    messages = storage.format_conversation(storage.retrieve_conversation(conversation_id, message_id)["conversation"])

    if message_id and message_id.strip() != "null":
        #if truncated, we need to add back the prompt, both in the storage and in the current messages list
        storage.append_conversation(conversation_id, prompt, "You")
        messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

    if model == "gpt-3.5-turbo":
        return openai_complete(model, messages)
    elif model == "MrEagle 7B":
        return eagle_complete(model, messages)
    elif model == "test":
        return test_complete(model, messages)

def get_model(model_name, model_version):
    model = models[model_name][model_version]
    return model

