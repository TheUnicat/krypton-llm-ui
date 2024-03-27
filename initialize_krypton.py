import os
import json


def initialize():
    # Ensure the krypton_storage directory exists
    storage_dir = 'krypton_storage'
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)

    # Check and initialize conversation.json
    conversation_path = os.path.join(storage_dir, 'conversations.json')
    if not os.path.exists(conversation_path):
        initial_conversation = [{
            "id": "OmJTAXqRQacAoXOhBj0LLGvLKrLsHFAH",
            "title": "Sample Conversation",
            "conversation": [
                {
                    "role": "You",
                    "message": "Hi ChatGPT!",
                    "timestamp": "2024-03-09T09:08:16.376732",
                    "id": "veqmaaicwfuOxpWP5UPFfU1fvUgefjxZ",
                    "image_data": []
                },
                {
                    "role": [
                    "ChatGPT",
                    "3.5",
                    "OpenAI"
                ],
                    "message": "Hi there! How may I assist you today?",
                    "timestamp": "2024-03-09T09:08:17.250722",
                    "id": "nP3hZgoCSHDe9IWNuomiaLLOQr4ShYMk",
                    "image_data": []
                }
            ]
        }]
        with open(conversation_path, 'w') as file:
            json.dump(initial_conversation, file, indent=4)

    # Check and initialize secrets.json
    secrets_path = os.path.join(storage_dir, 'secrets.json')
    if not os.path.exists(secrets_path):
        secrets_content = {
            "openai": "Your openai api key here",
            "fireworks": "Your fireworks api key here",
            "anthropic": "Your anthropic api key here",
            "google": "Your google api key here",
            "discord_bot_token": "You discord bot token here"
        }
        with open(secrets_path, 'w') as file:
            json.dump(secrets_content, file, indent=4)

    system_prompts_path = os.path.join(storage_dir, 'system_prompts.json')
    if not os.path.exists(system_prompts_path):
        system_prompts_content = {
            {
        "id": "123e4567e89b12d3a456426655440003",
        "title": "Uwuifier",
        "prompt": "You are an AI that uwuifies responses, talking in a cute uwuspeak manner with lots of owo and >w< expressions."
    }
        }
        with open(system_prompts_path, 'w') as file:
            json.dump(system_prompts_content, file, indent=4)

    # Check and initialize temp_image_storage.json and image_storage.json with empty dicts
    for json_file in ['temp_image_storage.json', 'image_storage.json']:
        path = os.path.join(storage_dir, json_file)
        if not os.path.exists(path):
            with open(path, 'w') as file:
                json.dump({}, file, indent=4)

