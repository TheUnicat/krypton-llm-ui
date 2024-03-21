import json
from flask import Blueprint, request, jsonify

# Blueprint setup
key_storage_bp = Blueprint('key_storage', __name__)

# File path
SECRETS_FILE = 'krypton_storage/secrets.json'
SETTINGS_FILE = 'krypton_storage/settings.json'

def get_test_mode():
    #if test is enabled use a lorem ipsum generator as AI
    with open("krypton_storage/test_mode.json", "r") as file:
        test_mode = json.load(file)["test_mode"]

    return test_mode

def get_keys():
    """Retrieve the keys from secrets.json."""
    try:
        with open(SECRETS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def store_keys(keys):
    """Store updated keys in secrets.json."""
    with open(SECRETS_FILE, 'w') as file:
        json.dump(keys, file)



@key_storage_bp.route('/api/keys', methods=['GET'])
def retrieve_keys():
    """API endpoint for retrieving API keys."""
    keys = get_keys()
    return jsonify(keys)

@key_storage_bp.route('/api/keys', methods=['POST'])
def update_keys():
    """API endpoint for updating API keys."""
    keys = request.json
    store_keys(keys)
    return jsonify({"message": "Keys updated successfully"}), 200

def get_settings():
    """Retrieve settings from settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def set_settings(setting_key, setting_value):
    """Set a specific setting in settings.json."""
    settings = get_settings()
    settings[setting_key] = setting_value
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=4)

@key_storage_bp.route('/api/settings/name', methods=['GET'])
def get_name():
    """API endpoint for retrieving user's name."""
    settings = get_settings()
    return jsonify({'name': settings.get('name', '')})

@key_storage_bp.route('/api/settings/name', methods=['POST'])
def set_name():
    """API endpoint for setting user's name."""
    name = request.json.get('name')
    if name is not None:
        set_settings('name', name)
        return jsonify({'message': 'Name updated successfully'}), 200
    return jsonify({'message': 'Invalid name'}), 400