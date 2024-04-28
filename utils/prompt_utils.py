import os
import json
from storage import generate_id

def fetch_sys_prompts():
    ids = find_recent_prompt_ids()
    prompts = []
    for id in ids:
        prompt_data = retrieve_sys_prompt(id)
        prompts.append(prompt_data)

    return prompts

def find_recent_prompt_ids():
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

def delete_sys_prompt(prompt_id):
    print(prompt_id)
    print("deelting")
    # Load the conversation data from the JSON file
    with open('krypton_storage/system_prompts.json', 'r') as file:
        prompts = json.load(file)

    # Also load the image data to prepare for possible image deletion
    # Assuming 'delete_image' function exists and operates on image_storage.json

    for prompt in prompts:
        if prompt["id"] == prompt_id:

            prompts = [prompt for prompt in prompts if prompt["id"] != prompt_id]

            # Save the updated conversations back to the JSON file
            with open('krypton_storage/system_prompts.json', 'w') as file:
                json.dump(prompts, file, indent=4)
            break  #


def select_sys_prompt(id):
    settings_path = 'krypton_storage/settings.json'
    # Ensure the directory exists
    with open(settings_path, 'r') as file:
        settings = json.load(file)

    # Update the current_sys_prompt
    settings['current_sys_prompt'] = id

    # Save the updated settings
    with open(settings_path, 'w') as file:
        json.dump(settings, file, indent=4)

    return True

def retrieve_current_sys_prompt():
    settings_path = 'krypton_storage/settings.json'
    # Ensure the directory exists
    with open(settings_path, 'r') as file:
        settings = json.load(file)

    return settings['current_sys_prompt']

def retrieve_current_sys_prompt_name():
    current_sys_prompt = retrieve_current_sys_prompt()
    if current_sys_prompt is None:
        return "null"
    return retrieve_sys_prompt(current_sys_prompt)["title"]

def update_or_add_system_prompt(id=None, title=None, text=None):
    filepath = 'krypton_storage/system_prompts.json'
    with open(filepath, 'r') as file:
        prompts = json.load(file)

        if id is None or id == "null":
            id = generate_id()
            prompts.insert(0,
                           {
                               "id": id,
                               "title": title,
                               "prompt": text
                           }
                           )
        else:
            for prompt in prompts:
                if prompt["id"] == id:
                    prompt["prompt"] = text
                    prompt["title"] = title
                    break

    with open(filepath, 'w') as file:
        json.dump(prompts, file, indent=4)

    return id