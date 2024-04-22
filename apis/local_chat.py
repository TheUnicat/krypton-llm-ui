# Uses the python wrapper for llama.cpp to integrate local models

from llama_cpp import Llama
from utils import model_utils
from os import path as ospath

global completion
global client_id
import json

global llm
llm = False


def load_model(path):
    global llm
    print(path)
    assert ospath.exists(path)
    llm = Llama(model_path=path, use_mlock=True,
                n_gpu_layers=1, seed=-1, n_ctx=768)
    return llm

#this is a function that completes a conversation between the user and the ai
#It adds a system message, then takes the first message and adds it to messages as an ai message, and then alternates between user and ai messages
def local_complete(model, messages, image_data=[], max_tokens=1000, system_prompt="", tools=[]):
    global llm

    messages = fit_to_grammar(messages, get_template(model[0]))
    model_info = model_utils.get_model_info(model)

    #load llm if needed
    if llm:
        pass
    else:
        llm = load_model(path="models/" + model_info["path"])

    # Start streaming from the LLM
    chunks = 0
    stream = llm(messages, max_tokens=max_tokens, stream=True)
    for output in stream:
        generated_text = output["choices"][0]["text"]
        chunks += 1
        yield generated_text



def get_template(model_name):
    with open("krypton_storage/models.json", "r") as file:
        models = json.load(file)
        print(models["Local"][model_name])
        template_name = models["Local"][model_name]["template"]

    with open("krypton_storage/prompt_templates.json", "r") as file:
        templates = json.load(file)
        template = templates[template_name]

    return template

def fit_to_grammar(messages, template):
    final_string = ""
    for msg in messages:
        role = msg["role"]  # Get the role of the message
        content = msg["content"]  # Get the content of the message
        formatted_message = template[role].replace("{message}", content)  # Replace {message} in template
        final_string += formatted_message  # Concat to the final string

    # Add the half-response template for the assistant's part
    assistant_template_half = template["assistant"].split("{message}")[0]
    final_string += assistant_template_half

    return final_string


