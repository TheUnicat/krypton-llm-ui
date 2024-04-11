from openai import OpenAI
import json
from utils import model_utils
from utils import tool_utils
from tool_handling import tool_handler

print("hi")

with open("krypton_storage/secrets.json", "r") as file:
    openai_key = json.load(file)["openai"]

client = OpenAI(api_key=openai_key)


def openai_complete(model, messages, images=None, max_tokens=4096, system_prompt=None, tools=None):
    model_name = model_utils.get_model(model)

    # Reformat messages to include image data if present
    updated_messages = []
    for message in messages[:-1]:
        if message.get("image_data") and len(message["image_data"]) > 0:
            new_content = [{"type": "text", "text": message["content"]}]
            for image_data in message["image_data"]:
                # Format the image data as a URL with base64 string
                base64_image = image_data["base64"]
                image_url = f"data:{image_data['mime']};base64,{base64_image}"
                new_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })
            updated_messages.append({"role": message["role"], "content": new_content})
        else:
            updated_messages.append(message)

    updated_messages.append(messages[-1])

    # Check if the images list is not empty and reformat accordingly
    if images:
        # Reformat the last message in the updated_messages list to include image URLs
        last_message = updated_messages[-1]
        new_content = [{"type": "text", "text": last_message["content"]}]
        for image_data in images:
            # Format the image data as a URL with base64 string
            base64_image = image_data["image"]
            image_url = f"data:{image_data['type']};base64,{base64_image}"
            new_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })
        updated_messages[-1] = {"role": "user", "content": new_content}

    if system_prompt:
        updated_messages.insert(0, {
            "role": "system",
            "content": system_prompt
        }
        )

    print(tools)
    completion = client.chat.completions.create(
        model=model_name,
        messages=updated_messages,
        stream=True,
        max_tokens=max_tokens,
        tools=tools
    )

    # Initialize variables to store streaming text content and function call details
    # Define variables to hold the streaming content and function call details
    function_call = {"name": "", "arguments": {}}
    argument_values_str = ""  # Accumulate all argument values in this string

    for chunk in completion:

        # Yield content if present
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

        tool_calls = chunk.choices[0].delta.tool_calls if chunk.choices[0].delta.tool_calls else []
        for tool_call in tool_calls:
            # Check for function name
            if tool_call.function.name:
                function_call["name"] = tool_call.function.name

            # Accumulate argument fragments
            if tool_call.function.arguments is not None:
                argument_values_str += tool_call.function.arguments

    print(argument_values_str)
    # Try to parse the accumulated argument values string into a dictionary
    try:
        if argument_values_str:
            # Ensure the string is a valid JSON object
            # This may need adjustment depending on how the fragments are formatted
            function_call["arguments"] = json.loads(argument_values_str)
    except json.JSONDecodeError as e:

        print(f"Error parsing arguments JSON: {e}")

    # After processing all chunks, print the function call details
    if function_call["name"]:
        print(f"Function call requested: {function_call['name']} with arguments {function_call['arguments']}")
        result = None
        for result_prototype in tool_handler(function_call["name"], function_call["arguments"]):
            print(result_prototype)
            result_prototype = json.loads(result_prototype)
            print("IS RESULT")
            yield f"[TOOL_USE]{{\"tool_name\": \"{function_call['name']}\", \"query\": \"{function_call['arguments']}\", \"tool_result\": \"{result_prototype['result']}\", \"is_open\": {json.dumps(result_prototype['done'])}}}[/TOOL_USE]\n\n"
            result = result_prototype['result']


        messages.append({"role": "assistant", "content": f"{function_call['name']} with arguments {function_call['arguments']}"})
        messages.append({"role": "user", "content": result})
        print(messages)
        import time
        time.sleep(5)
        for chunk in openai_complete(model, messages, [], max_tokens, system_prompt, tools):
            yield chunk
    else:
        print("No function call in the response.")

