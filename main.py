from flask import Flask, send_from_directory, Response, jsonify, request
from openai_chat import openai_complete
from openai_chat import openai_test
#from eagle_chat import eagle_complete
import storage
import json
from titles import make_title


app = Flask(__name__, static_url_path='', static_folder='static')

with open("models.json", "r") as file:
    models = json.load(file)

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


@app.route('/stream')
def stream():
    conversation_id = request.args.get('id')
    prompt = request.args.get('prompt')  # Capture the 'prompt' query parameter as a string
    model_name = request.args.get('model_name')
    model_version = request.args.get('model_version')
    message_id = request.args.get('model_id')

    model = models[model_name][model_version]

    print("Prompt ", prompt)
    print("conversation id ", conversation_id)
    print("model ", model)

    #if new conversation, make a title
    new_convo = False

    if conversation_id is not None and conversation_id != "null":
        message_id = storage.append_conversation(conversation_id, prompt, "You")
    else:
        conversation_id, message_id = storage.create_conversation(prompt)
        new_convo = True

    def generate(model, prompt, conversation_id, message_id):
        try:
            yield f"data: {{\"conversation_id\": \"{conversation_id}\", \"message_id\": \"{message_id}\"}}\n\n"
            # Accumulate responses from the generator
            accumulated_response = ""
            if model == "gpt-3.5-turbo":
                for response in openai_complete(model, prompt, conversation_id, message_id):
                    if response:
                        accumulated_response += response
                        yield f"data: {response}\n\n"
            else:
                for response in eagle_complete(model, prompt, conversation_id):
                    if response:
                        accumulated_response += response
                        yield f"data: {response}\n\n"

            # Once generation is complete, append the whole conversation
            if conversation_id and accumulated_response:
                print(accumulated_response)
                storage.append_conversation(conversation_id, accumulated_response, model)
                if new_convo:
                    storage.rename(conversation_id, make_title(prompt, accumulated_response))

        except Exception as e:
            error_message = str(e)
            print("An error occurred: ", error_message)
            # Return a JSON response with the error attribute
            yield f"data: {{\"error\": \"{error_message}\"}}\n\n"

    return Response(generate(model, prompt, conversation_id, message_id), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port="8080")
