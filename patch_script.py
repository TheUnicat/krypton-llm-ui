import json
import image_storage

with open("krypton_storage/conversations.json", "r") as file:
    data = json.load(file)

    for conversation in data:

        for message in conversation["conversation"]:
            image_data = message["image_data"]
            if image_data != [] and image_data != ["yFvajzadm3dDAmswqdM8kE0VUd2rAyHf"]:
                for image in image_data:
                    image_storage.delete_image(image)
                message["image_data"] = []


with open("krypton_storage/conversations.json", "w") as file:
    json.dump(data, file, indent=4)