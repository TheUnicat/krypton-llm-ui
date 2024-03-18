import json
import traceback
from flask import Flask, send_from_directory, Response, jsonify, request

import storage
import ai
import store_images
from store_images import process_and_store_images

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/get_recent_conversations')
def get_recent_conversations():
    return storage.fetch_recent_conversations()

@app.route('/delete_conversation')
def delete_conversation():
    conversation_id = request.args.get('id')
    storage.delete_conversation(conversation_id)
    return "200"

@app.route('/rename_conversation')
def rename_conversation():
    conversation_id = request.args.get('id')
    new_name = request.args.get('new_name')
    storage.rename_conversation(conversation_id, new_name)
    return "200"

@app.route('/retrieve_conversation')
def retrieve_conversation():
    # Assume we have a function to get conversation by ID
    conversation_id = request.args.get('id')
    conversation = storage.retrieve_conversation(conversation_id, should_load_images=True)

    return jsonify(conversation)

def print_error_with_traceback(error_message):
    print("An error occurred: ", error_message)
    traceback.print_exc()

@app.route('/stream')
def stream():
    conversation_id = request.args.get('id')
    prompt = request.args.get('prompt')  # Capture the 'prompt' query parameter as a string
    model_name = request.args.get('model_name')
    model_version = request.args.get('model_version')
    message_id_for_edit = request.args.get('message_id')
    api = request.args.get('api')
    has_images = request.args.get('images')
    print(has_images)
    print("has image?")

    new_convo = False

    if has_images == "true" or has_images is True:
        image_data = store_images.load_images()
    else:
        image_data = []

    if conversation_id is not None and conversation_id != "null":
        message_id = storage.append_conversation(conversation_id, prompt, "You", image_data)
    else:
        conversation_id, message_id = storage.create_conversation(prompt, image_data)
        new_convo = True


    def generate(api, prompt, conversation_id, message_id):
        combined_model_info = [model_name, model_version, api]

        try:
            accumulated_response = ""
            yield f"data: {{\"conversation_id\": \"{conversation_id}\", \"message_id\": \"{message_id}\"}}\n\n"
            for response in ai.format_to_chat(combined_model_info, prompt, conversation_id, message_id_for_edit, image_data):
                if response:
                    # Replace newlines for correct client-side handling
                    response = response.replace("\n", "\\n")
                    accumulated_response += response
                    yield f"data: {accumulated_response}\n\n"
        except Exception as e:
            error_message = str(e)
            print("An error occurred: ", error_message)
            print_error_with_traceback(str(e))

            yield f"data: {{\"error\": \"{error_message}\"}}\n\n"
            return

        # If needed, handle the storage append and rename operations here, outside of the try-except block
        if conversation_id and accumulated_response:
            storage.append_conversation(conversation_id, accumulated_response, combined_model_info)
            if new_convo:
                new_title = ai.make_title(combined_model_info, prompt, accumulated_response)
                storage.rename_conversation(conversation_id, new_title)
                yield f"data: {{\"new_title\": \"{new_title}\"}}\n\n"

    return Response(generate(api, prompt, conversation_id, message_id), mimetype='text/event-stream')

@app.route("/get_models_html")
def get_models_html():
    with open("krypton_storage/models.json", "r") as file:
        models_data = json.load(file)

    dropdown_html = ""

    # Iterate over APIs
    for api, api_info in models_data.items():
        # Iterate over product families within each API
        for product_family, family_info in api_info.items():
            # Now iterate over model versions within each product family
            if not type(family_info) == dict:
                continue
            for model_version in family_info:
                model_display_name = f"{api} - {product_family} - {model_version}"
                dropdown_html += f'<div style="cursor: pointer;" onclick="changeModel(\'{api}\', \'{product_family}\', \'{model_version}\')">{model_display_name}</div>\n'

    # Append the additional div for "Add Model" at the end
    dropdown_html += '<div style="cursor: pointer;" onclick="addModel()">Add Model</div>\n'

    return Response(dropdown_html, mimetype='text/html')


@app.route('/upload_images', methods=['POST'])
def upload_images():
    if 'images' not in request.files:
        return jsonify({'error': 'No images part'}), 400

    images = request.files.getlist('images')

    if not images:
        return jsonify({'error': 'No selected file'}), 400

    process_and_store_images(images)

    return jsonify({'message': 'Images uploaded and saved successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port="8080")
