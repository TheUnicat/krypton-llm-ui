import json
import os

# The path to the JSON file
json_file_path = 'krypton_storage/image_storage.json'

def load_data():
    """Load the data from the JSON file."""
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_data(data):
    """Save the data to the JSON file."""
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def store_image(mime, base64_str, id):
    """Store an image with the given MIME type, base64 string, and ID."""
    data = load_data()
    data[id] = {'mime': mime, 'base64': base64_str}
    save_data(data)

def retrieve_image(id):
    """Retrieve an image by its ID."""
    data = load_data()
    return data.get(id)

