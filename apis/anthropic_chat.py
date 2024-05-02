import json
import anthropic
from utils import model_utils
from typing import Dict, List
from utils import tool_utils
from tool_handling import tool_handler


def format_tools(schemas: List[Dict]) -> List[Dict]:
    converted_schemas = []

    for schema in schemas:
        if schema["type"] == "function":
            function_schema = schema["function"]
            converted_schema = {
                "name": function_schema["name"],
                "description": function_schema["description"],
                "input_schema": function_schema["parameters"]
            }
            converted_schemas.append(converted_schema)

    return converted_schemas


def anthropic_complete(model, messages, images=[], max_tokens=4096, system_prompt=None, tools=[]):

    with open("krypton_storage/secrets.json", "r") as file:
        anthropic_key = json.load(file)["anthropic"]

    client = anthropic.Anthropic(
        api_key=anthropic_key
    )

    unformatted_tools = tools
    tools = format_tools(tools)
    model_name = model_utils.get_model(model)

    # Reformat messages to include image data if present
    updated_messages = []
    for message in messages[:-1]:
        if message.get("image_data") and len(message["image_data"]) > 0:
            new_content = [{"type": "text", "text": message["content"]}]
            for image_data in message["image_data"]:
                new_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_data["mime"],
                        "data": image_data["base64"]
                    }
                })
            updated_messages.append({"role": message["role"], "content": new_content})
        else:
            updated_messages.append(message)

    updated_messages.append(messages[-1])

    # Check if the images list is not empty
    if images:
        # Reformat the last message in the updated_messages list to include image data
        last_message = updated_messages[-1]
        new_content = [{"type": "text", "text": last_message["content"]}]
        for image_data in images:
            new_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_data["type"],
                    "data": image_data["image"]
                }
            })
        updated_messages[-1] = {"role": "user", "content": new_content}

    # Continue with your existing logic for streaming messages
    if tools == []:
        if system_prompt is not None:
            with client.messages.stream(
                max_tokens=max_tokens,
                messages=updated_messages,
                model=model_name,
                system=system_prompt
            ) as stream:
                for text in stream.text_stream:
                    yield text
        else:
            with client.messages.stream(
                max_tokens=max_tokens,
                messages=updated_messages,
                model=model_name
            ) as stream:
                for text in stream.text_stream:
                    yield text
    else:
        if system_prompt is not None:
            response = client.beta.tools.messages.create(
                max_tokens=max_tokens,
                messages=updated_messages,
                model=model_name,
                system=system_prompt,
                tools=tools
            )
        else:
            response = client.beta.tools.messages.create(
                max_tokens=max_tokens,
                messages=updated_messages,
                model=model_name,
                tools=tools
            )

        print(response)


        used_tool = False

        for item in response.content:
            if item.type == "text":
                yield item.text
            elif item.type == "tool_use":
                used_tool = True

                for result_prototype in tool_handler(item.name, item.input):
                    result_prototype = json.loads(result_prototype)
                    yield f"[TOOL_USE]{{\"tool_name\": \"{item.name}\", \"query\": \"{item.input}\", \"tool_result\": \"{result_prototype['result']}\", \"is_open\": {json.dumps(result_prototype['done'])}}}[/TOOL_USE]\n\n"

        if used_tool:
            for chunk in anthropic_complete(model, messages, tools=unformatted_tools, max_tokens=max_tokens, system_prompt=system_prompt, images=images):
                yield chunk
