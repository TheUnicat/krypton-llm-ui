import json
import os
import random
import string
import datetime


nicknames = {"gpt-3.5-turbo": "ChatGPT"}

def generate_id(size=32, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def create_conversation(message):
    conversation_id = generate_id()
    message_id = generate_id()
    title = "New Chat"
    timestamp = datetime.datetime.utcnow().isoformat()
    conversation = {
        "id": conversation_id,
        "title": title,
        "conversation": [{"role": "You", "message": message, "timestamp": timestamp, "id": message_id}]
    }
    if not os.path.isfile("conversations.json"):
        with open("conversations.json", "w") as file:
            json.dump([conversation], file, indent=4)
    else:
        with open("conversations.json", "r+") as file:
            data = json.load(file)
            data.append(conversation)
            file.seek(0)
            json.dump(data, file, indent=4)
    return conversation_id, message_id


def append_conversation(conversation_id, message, author):
    if not os.path.isfile("conversations.json"):
        return None

    message_id = generate_id()
    with open("conversations.json", "r+") as file:
        data = json.load(file)
        for conversation in data:
            if conversation["id"] == conversation_id:
                timestamp = datetime.datetime.utcnow().isoformat()
                conversation["conversation"].append({"role": author, "message": message, "timestamp": timestamp, "id": message_id})
                break
        else:  # If the conversation ID was not found
            return None
        file.seek(0)
        file.truncate()
        json.dump(data, file, indent=4)
    return message_id

def find_recent_conversation_ids(n=5):
    if not os.path.isfile("conversations.json"):
        return None
    with open("conversations.json", "r") as file:
        data = json.load(file)
        # Sort the conversations based on the timestamp of the last message
        sorted_conversations = sorted(data, key=lambda x: x["conversation"][-1]["timestamp"], reverse=True)
        # Extract the IDs of the n most recent conversations
        recent_conversations_ids = [conv["id"] for conv in sorted_conversations[:n]]
    return recent_conversations_ids

def retrieve_conversation(id, message_id=None):
    # Check if the file exists
    if not os.path.isfile("conversations.json"):
        return None

    if message_id is not None and message_id.strip() != "null":
        print("1",message_id,"2")
        truncate_conversation_at_message(id, message_id)
        print("TRUNCATED")

    with open("conversations.json", "r") as file:
        data = json.load(file)
        for conversation in data:
            if conversation["id"] == id:
                try:
                    for message in conversation["conversation"]:
                        if message["role"] in nicknames:
                            message["role"] = nicknames[message["role"]]
                except Exception as e:
                    print(e)

                return conversation
    return None


def fetch_recent_conversations(n=5):
    ids = find_recent_conversation_ids(n)
    conversations = []
    for id in ids:
        conversations.append(retrieve_conversation(id))

    return conversations

def format_conversation(conversation):
    simplified_messages = []

    for message in conversation:
        author = message['role'].lower()  # Convert to lowercase for easier comparison
        role = 'assistant'  # Default role

        if author in ['user', 'you']:
            role = 'user'
        elif author in ['system', 'system']:
            role = 'system'


        simplified_messages.append({"role": role, "content": message["message"]})

    return simplified_messages

def truncate_conversation_at_message(id, message_id):
    # Check if the file exists
    if not os.path.isfile("conversations.json"):
        print("File not found.")
        return False

    with open("conversations.json", "r") as file:
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
        print("Conversation not found.")
        return False

    with open("conversations.json", "w") as file:
        json.dump(data, file, indent=4)

    return True


def rename(conversation_id, new_title):
    with open("conversations.json", "r") as file:
        data = json.load(file)
        for conversation in data:
            if conversation["id"] == conversation_id:
                conversation["title"] = new_title
                break  # Stops the loop once the matching conversation is found and updated

    with open("conversations.json", "w") as file:
        json.dump(data, file, indent=4)

