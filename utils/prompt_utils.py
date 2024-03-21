import os
import json

def fetch_sys_prompts(n=1000):
    ids = find_recent_conversation_ids(n)
    prompts = []
    for id in ids:
        prompt_data = retrieve_sys_prompt(id)
        prompts.append(prompt_data)

    return prompts

def find_recent_conversation_ids():
    if not os.path.isfile("krypton_storage/system_prompts.json"):
        return None
    with open("krypton_storage/system_prompts.json", "r") as file:
        data = json.load(file)

        return [message["id"] for message in data]

def retrieve_sys_prompt(id):
    # Check if the file exists
    if not os.path.isfile("krypton_storage/system_prompts.json"):
        return None

    with open("krypton_storage/system_prompts.json", "r") as file:
        data = json.load(file)
        for prompt in data:
            if prompt["id"] == id:
                return prompt

    return None
