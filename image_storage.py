import base64
import mimetypes
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


def delete_image(id):
    """Delete an image by its ID."""
    # Load the current data from the JSON file
    data = load_data()

    # Check if the image id exists in the data. If it does, remove it and savee
    if id in data:
        del data[id]
        save_data(data)
        return True

def convert_image_to_base64(image):
    """Converts an image to base64 and returns it along with the MIME type."""
    mime_type, _ = mimetypes.guess_type(image.name)
    # Default to 'application/octet-stream' if MIME type couldn't be guessed
    mime_type = mime_type or 'image/png'
    image_string = base64.b64encode(image.read()).decode('utf-8')
    return image_string, mime_type

def temporarily_save_images(base64_images_with_type):
    """Saves a list of base64 encoded images with their MIME types to a JSON file."""
    storage_path = "krypton_storage/temp_image_storage.json"
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)  # Ensure directory exists
    with open(storage_path, 'w') as file:
        # Convert the list of tuples into a list of dictionaries for JSON serialization
        images_data = [{"image": image[0], "type": image[1]} for image in base64_images_with_type]
        json.dump(images_data, file)

def process_and_store_images(images):
    """Converts and stores images along with their MIME types."""
    base64_images_with_type = [convert_image_to_base64(image) for image in images]
    temporarily_save_images(base64_images_with_type)

def load_images():
    """Loads and decodes base64 encoded images and their MIME types from a JSON file."""
    storage_path = "krypton_storage/temp_image_storage.json"
    try:
        with open(storage_path, 'r') as file:
            base64_images_with_type = json.load(file)
            # If you need the binary data of images, you can decode them here. Example:
            # images_data = [{"data": base64.b64decode(img["image"]), "type": img["type"]} for img in base64_images_with_type]
            # return images_data
            return base64_images_with_type  # Returns the list of dictionaries with base64 encoded image strings and MIME types
    except FileNotFoundError:
        # Handle the case where the JSON file doesn't exist
        print("No stored images found.")
        return []
    except json.JSONDecodeError:
        # Handle the case where the JSON is malformed
        print("Error decoding JSON from the file.")
        return []


