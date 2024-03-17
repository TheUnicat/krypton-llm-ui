import base64
import json
import os

def convert_image_to_base64(image):
    """Converts an image to base64."""
    image_string = base64.b64encode(image.read()).decode('utf-8')
    return image_string

def save_images_to_json(base64_images):
    """Saves a list of base64 encoded images to a JSON file."""
    storage_path = "krypton_storage/temp_image_storage.json"
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)  # Ensure directory exists
    with open(storage_path, 'w') as file:
        json.dump(base64_images, file)

def process_and_store_images(images):
    """Converts and stores images."""
    base64_images = [convert_image_to_base64(image) for image in images]
    save_images_to_json(base64_images)
