import json

with open("krypton_storage/conversations.json", "r") as file:
    data = json.load(file)

for conversation in data:

    for message in conversation["conversation"]:
        print(message)
        try:
            image_data = message["image_data"]
        except:
            message["image_data"] = []

json.dump(data, "krypton_storage/conversations.json", indent=4)