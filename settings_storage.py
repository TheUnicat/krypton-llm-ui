import json
from flask import Blueprint, request, jsonify

# Blueprint setup
key_storage_bp = Blueprint('key_storage', __name__)

# File path
SECRETS_FILE = 'krypton_storage/secrets.json'

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
