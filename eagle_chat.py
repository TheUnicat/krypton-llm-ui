from llama_cpp import Llama
import storage

def load_model():
    global llm
    llm = Llama(model_path="/Users/hongyang/Downloads/text-generation-webui/models/MrEagle-Q4_K_M.gguf", use_mlock=True,#Vera-Q4_K_M.gguf", use_mlock=True,
                n_gpu_layers=1, seed=-1, n_ctx=768)

load_model()

global completion
global client_id


#this is a function that completes a conversation between the user and a writing/text understanding AI, WriteGPT
#It adds a system message, then takes the first message and adds it to messages as an ai message, and then alternates between user and ai messages
def generate(prompt, max_tokens):
    previous_tool_index = -1
    round = 1
    cumulated_text = prompt
    if llm:
        while True:
            print("round", round)
            round += 1
            if round == 3:
                return

            # Start streaming from the LLM
            if True:
                #load_model()
                chunks = 0
                done = False
                while not done:
                    stream = llm(prompt, max_tokens=max_tokens, stream=True)
                    for output in stream:
                        generated_text = output["choices"][0]["text"]
                        cumulated_text += generated_text
                        chunks += 1
                        yield generated_text

                    if chunks > 0:
                        done = True

    else:
        yield "Error: LLM not available"


# Function to complete the chat using the generator
def chat_complete(prompt, max_tokens):
    #print("hi")
    try:
        response_stream = generate(prompt, max_tokens)
        for response in response_stream:
            #print(response)
            yield response
    except Exception as e:
        print(e)
        yield "Sorry, there seems to be a server problem right now and the AI is currently unavailable. Please try again later."

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

