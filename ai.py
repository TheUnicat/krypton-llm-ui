import json

import storage
from utils import model_utils
from utils.settings_utils import get_test_mode
from apis.openai_chat import openai_complete
from apis.test_chat import test_complete
from apis.local_chat import local_complete
from apis.fireworks_chat import fireworks_complete
from apis.anthropic_chat import anthropic_complete

test_mode = get_test_mode()

with open("krypton_storage/models.json", "r") as file:
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

    if test_mode:
        return test_complete(model, messages)

    model_api = model[2].lower()

    function_name = f"{model_api}_complete"

    # Get the function from globals() based on constructed function name
    complete_function = globals().get(function_name)

    if complete_function:
        return complete_function(model, messages)
    else:
        raise ValueError(f"No completion function found for API: {model_api}")


def make_title(model, user_message, ai_response):
    # Format the messages as per the specified structure
    messages = [{
        "role": "user",
        "content": f"""
        "User: {user_message}\nAI: {ai_response}"

        "Make a short title, no more than a few words, for this conversation, in same language as the conversation."
        """
    }]

    #get the appropriate API for completion
    model_api = model[2].lower()
    function_name = f"{model_api}_complete"

    # Retrieve the global completion function based on the model's API
    complete_function = globals().get(function_name)

    if complete_function:
        new_title = ""
        for response in complete_function(model, messages, max_tokens=30):
            if response:
                new_title += response

        #return after escaping quotes and stripping quotes
        return new_title.strip('"').replace('"', '\\"')
    else:
        # If no specific completion function is found, raise an error
        raise ValueError(f"No completion function found for API: {model_api}")

