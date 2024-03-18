import json

with open("krypton_storage/conversations.json", "r") as file:
    data = json.load(file)

    for conversation in data:

        for message in conversation["conversation"]:
            try:
                image_data = message["image_data"]
            except:
                print("hi")
                message["image_data"] = []

with open("krypton_storage/conversations.json", "w") as file:
    json.dump(data, file, indent=4)