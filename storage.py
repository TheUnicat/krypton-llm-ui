import json
import os
import random
import string
import datetime
from utils.settings_utils import get_test_mode
import image_storage

test_mode = get_test_mode()

nicknames = {"gpt-3.5-turbo": "ChatGPT"}


def generate_id(size=32, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_conversation(message, image_data=[]):
    conversation_id = generate_id()
    message_id = generate_id()
    title = "New Chat"
    timestamp = datetime.datetime.utcnow().isoformat()

    list_of_image_ids = []

    if image_data != []:
        for image in image_data:
            image_id = generate_id()
            image_storage.store_image(image["type"], image["image"], image_id)
            list_of_image_ids.append(image_id)

    conversation = {
        "id": conversation_id,
        "title": title,
        "conversation": [{"role": "You", "message": message, "timestamp": timestamp, "id": message_id, "image_data": list_of_image_ids}]
    }
    if not os.path.isfile("krypton_storage/conversations.json"):
        with open("krypton_storage/conversations.json", "w") as file:
            json.dump([conversation], file, indent=4)
    else:
        with open("krypton_storage/conversations.json", "r+") as file:
            data = json.load(file)
            data.append(conversation)
            file.seek(0)
            json.dump(data, file, indent=4)
    return conversation_id, message_id


def append_conversation(conversation_id, message, author, image_data=[]):
    if not os.path.isfile("krypton_storage/conversations.json"):
        return None

    message_id = generate_id()
    with open("krypton_storage/conversations.json", "r+") as file:
        data = json.load(file)
        for conversation in data:
            if conversation["id"] == conversation_id:
                timestamp = datetime.datetime.utcnow().isoformat()

                list_of_image_ids = []
                if image_data != []:
                    for image in image_data:
                        image_id = generate_id()
                        image_storage.store_image(image["type"], image["image"], image_id)
                        list_of_image_ids.append(image_id)

                conversation["conversation"].append({"role": author, "message": message, "timestamp": timestamp, "id": message_id, "image_data": list_of_image_ids})
                break

        else:  # If the conversation ID was not found
            return None
        file.seek(0)
        file.truncate()
        json.dump(data, file, indent=4)
    return message_id

def find_recent_conversation_ids(n=20):
    if not os.path.isfile("krypton_storage/conversations.json"):
        return None
    with open("krypton_storage/conversations.json", "r") as file:
        data = json.load(file)
        # Sort the conversations based on the timestamp of the last message
        sorted_conversations = sorted(data, key=lambda x: x["conversation"][-1]["timestamp"], reverse=True)
        # Extract the IDs of the n most recent conversations
        recent_conversations_ids = [conv["id"] for conv in sorted_conversations[:n]]
    return recent_conversations_ids

def retrieve_conversation(id, message_id=None, should_load_images=False):
    # Check if the file exists
    if not os.path.isfile("krypton_storage/conversations.json"):
        return None

    if message_id is not None and message_id.strip() != "null":
        truncate_conversation_at_message(id, message_id)

    with open("krypton_storage/conversations.json", "r") as file:
        data = json.load(file)
        for conversation in data:
            if conversation["id"] == id:
                return conversation if not should_load_images else load_images(conversation)

    return None


def fetch_recent_conversations(n=20):
    ids = find_recent_conversation_ids(n)
    conversations = []
    for id in ids:
        conversation_data = retrieve_conversation(id)
        conversation_data.pop('conversation', None)  # Remove the 'conversation' attribute if it exists
        conversations.append(conversation_data)

    return conversations

def format_conversation(conversation):
    simplified_messages = []

    for message in conversation:
        author = message['role'].lower() if type(message['role']) == str else message['role']  # Convert to lowercase for easier comparison
        role = 'assistant'  # Default role

        if author in ['user', 'you']:
            role = 'user'
        elif author in ['system', 'system']:
            role = 'system'

        simplified_messages.append({"role": role, "content": message["message"]})

    return simplified_messages

def truncate_conversation_at_message(id, message_id):
    # Check if the file exists
    if not os.path.isfile("krypton_storage/conversations.json"):
        return False

    with open("krypton_storage/conversations.json", "r") as file:
        data = json.load(file)

    conversation_found = False
    for conversation in data:
        if conversation["id"] == id:
            conversation_found = True
            new_conversation = []
            for message in conversation["conversation"]:
                if message["id"] == message_id:
                    break
                new_conversation.append(message)
            # Update the conversation with the truncated version
            conversation["conversation"] = new_conversation
            break

    if not conversation_found:
        return False

    with open("krypton_storage/conversations.json", "w") as file:
        json.dump(data, file, indent=4)

    return True


def rename_conversation(conversation_id, new_title):
    with open("krypton_storage/conversations.json", "r") as file:
        data = json.load(file)
        for conversation in data:
            if conversation["id"] == conversation_id:
                conversation["title"] = new_title
                break  # Stops the loop once the matching conversation is found and updated

    with open("krypton_storage/conversations.json", "w") as file:
        json.dump(data, file, indent=4)


def delete_conversation(conversation_id):
    # Load the conversation data from the JSON file
    with open('krypton_storage/conversations.json', 'r') as file:
        conversations = json.load(file)

    # Find and remove the conversation with the specified ID
    conversations = [conversation for conversation in conversations if conversation["id"] != conversation_id]

    # Save the updated conversations back to the JSON file
    with open('krypton_storage/conversations.json', 'w') as file:
        json.dump(conversations, file, indent=4)

def load_images(conversation):
    for message in conversation["conversation"]:
        # Check if image_data is not empty
        try:
            if message["image_data"]:
                # Replace each ID in image_data with the actual image data from image_storage
                message["image_data"] = [image_storage.retrieve_image(image_id) for image_id in message["image_data"]]
        except:
            return conversation

    return conversation
