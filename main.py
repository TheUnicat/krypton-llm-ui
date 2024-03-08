from flask import Flask, send_from_directory, Response, jsonify, request
from openai_chat import openai_complete
from openai_chat import openai_test
#from eagle_chat import eagle_complete
import storage


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


@app.route('/stream')
def stream():
    conversation_id = request.args.get('id')
    prompt = request.args.get('prompt')  # Capture the 'prompt' query parameter as a string
    model = request.args.get('model')
    print("Prompt ", prompt)
    print("conversation id ", conversation_id)
    print("model ", model)
    if conversation_id is not None and conversation_id != "null":
        storage.append_conversation(conversation_id, prompt, "You")
    else:
        conversation_id = storage.create_conversation(prompt)


    def generate(model, prompt, conversation_id):
        yield f"data: {{\"conversation_id\": \"{conversation_id}\"}}\n\n"
        # Accumulate responses from the generator
        accumulated_response = ""
        if model == "gpt-3.5-turbo":
            for response in openai_complete(model, prompt, conversation_id):
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


    return Response(generate(model, prompt, conversation_id), mimetype='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port="8080")
