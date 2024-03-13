from flask import Flask, send_from_directory, Response, jsonify, request
import storage
import json
import utils
from titles import make_title
import traceback

app = Flask(__name__, static_url_path='', static_folder='static')


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/get_recent_conversations')
def get_recent_conversations():
    return storage.fetch_recent_conversations()

@app.route('/retrieve_conversation')
def retrieve_conversation():
    # Assume we have a function to get conversation by ID
    conversation_id = request.args.get('id')
    conversation = storage.retrieve_conversation(conversation_id)
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
    print(message_id_for_edit)

    new_convo = False

    if conversation_id is not None and conversation_id != "null":
        message_id = storage.append_conversation(conversation_id, prompt, "You")
    else:
        conversation_id, message_id = storage.create_conversation(prompt)
        new_convo = True

    def generate(model, prompt, conversation_id, message_id):
        try:
            accumulated_response = ""
            yield f"data: {{\"conversation_id\": \"{conversation_id}\", \"message_id\": \"{message_id}\"}}\n\n"
            for response in utils.format_to_chat([model_name, model_version], prompt, conversation_id, message_id_for_edit):
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

        # If needed, handle the storage append and rename operations here, outside of the try-except block
        if conversation_id and accumulated_response:
            storage.append_conversation(conversation_id, accumulated_response, utils.get_model(model_name, model_version))
            if new_convo:
                new_title = make_title(prompt, accumulated_response)
                storage.rename(conversation_id, new_title)
                yield f"data: {{\"new_title\": \"{new_title}\"}}\n\n"

    return Response(generate([], prompt, conversation_id, message_id), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port="8080")
