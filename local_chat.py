from llama_cpp import Llama
import storage
global completion
global client_id



def load_model(path):
    global llm
    llm = Llama(model_path=path, use_mlock=True,#Vera-Q4_K_M.gguf", use_mlock=True,
                n_gpu_layers=1, seed=-1, n_ctx=768)

#this is a function that completes a conversation between the user and the ai
#It adds a system message, then takes the first message and adds it to messages as an ai message, and then alternates between user and ai messages
def local_complete(messages, max_tokens):
    if llm:
        # Start streaming from the LLM
        if True:
            chunks = 0
            stream = llm(messages, max_tokens=max_tokens, stream=True)
            for output in stream:
                generated_text = output["choices"][0]["text"]
                chunks += 1
                yield generated_text
    else:
        yield "Error: LLM not available"




# Function to process the entire conversation
def eagle_complete(model, prompt, conversation_id):
    conversation_string = ""

    conversation = storage.format_conversation(storage.retrieve_conversation(conversation_id)["conversation"])

    for message in conversation:
        if message["role"] != "You":  # AI messages
            conversation_string += "\n### RESPONSE:\n\n" + message["content"]
        else:
            conversation_string += "\n### INPUT:\n\n" + message["content"]

    conversation_string += "\n\n### RESPONSE:\n"
    if len(conversation) > 2:
        conversation_string = " " + conversation_string

    return chat_complete(conversation_string, 400)

