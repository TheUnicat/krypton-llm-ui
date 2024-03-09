import storage
from openai_chat import openai_complete
#from eagle_chat import eagle_complete

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

    if model == "gpt-3.5-turbo":
        return openai_complete(model, messages)
    else:
        return eagle_complete(model, messages)

