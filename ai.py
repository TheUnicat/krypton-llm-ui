import storage
import utils
import json
from openai_chat import openai_complete
from test import test_complete
from local_chat import local_complete

with open("test_mode.json", "r") as file:
    test_mode = json.load(file)["test_mode"]
    print(test_mode)

with open("models.json", "r") as file:
    models = json.load(file)

def format_to_chat(model, prompt, conversation_id, message_id):
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


    print(model)

    model_name = utils.get_model(model[0], model[1])

    if test_mode:
        model_name = "test"

    if model_name == "gpt-3.5-turbo":
        return openai_complete(model, messages)
    elif utils.is_local_model(model[0], model[1]):
        print("locally completing")
        return local_complete(model, messages)
    elif model_name == "test":
        return test_complete(model, messages)

