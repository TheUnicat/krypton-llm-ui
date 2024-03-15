import storage
import utils
import json
from apis.openai_chat import openai_complete
from apis.test_chat import test_complete
from apis.local_chat import local_complete
from apis.fireworks_chat import fireworks_complete

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

    if test_mode:
        return test_complete(model, messages)


    model_family_info = utils.get_model_family_info(model[0])
    model_api = model_family_info["api"]
    function_name = f"{model_api}_complete"

    # Get the function from globals() based on constructed function name
    complete_function = globals().get(function_name)

    if complete_function:
        return complete_function(model, messages)
    else:
        raise ValueError(f"No completion function found for API: {model_api}")
