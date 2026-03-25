import json
import cohere
from utils import model_utils
from utils import tool_utils
from tool_handling import tool_handler


def format_tools(schemas):
    """Convert OpenAI-style tool schemas to Cohere format."""
    converted = []
    for schema in schemas:
        if schema["type"] == "function":
            func = schema["function"]
            converted.append({
                "type": "function",
                "function": {
                    "name": func["name"],
                    "description": func["description"],
                    "parameters": func["parameters"]
                }
            })
    return converted


def cohere_complete(model, messages, images=None, max_tokens=4096, system_prompt=None, tools=None):
    with open("krypton_storage/secrets.json", "r") as file:
        cohere_key = json.load(file)["cohere"]

    client = cohere.ClientV2(api_key=cohere_key)

    model_name = model_utils.get_model(model)

    # Build messages in Cohere v2 chat format (OpenAI-compatible)
    updated_messages = []

    if system_prompt:
        updated_messages.append({
            "role": "system",
            "content": system_prompt
        })

    for message in messages:
        updated_messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    cohere_tools = format_tools(tools) if tools else None

    response = client.chat_stream(
        model=model_name,
        messages=updated_messages,
        max_tokens=max_tokens,
        tools=cohere_tools if cohere_tools else None
    )

    function_call = {"name": "", "arguments": ""}

    for event in response:
        if event.type == "content-delta":
            if hasattr(event, 'delta') and hasattr(event.delta, 'message'):
                text = event.delta.message.content.text if hasattr(event.delta.message, 'content') else None
                if text:
                    yield text
            elif hasattr(event, 'delta') and hasattr(event.delta, 'content'):
                # Cohere SDK v2 streaming format
                text = event.delta.content
                if text:
                    yield text
        elif event.type == "tool-call-start":
            if hasattr(event, 'delta') and hasattr(event.delta, 'tool_call'):
                function_call["name"] = event.delta.tool_call.name
        elif event.type == "tool-call-delta":
            if hasattr(event, 'delta') and hasattr(event.delta, 'tool_call'):
                if hasattr(event.delta.tool_call, 'arguments'):
                    function_call["arguments"] += event.delta.tool_call.arguments

    # Handle tool calls
    if function_call["name"]:
        try:
            args = json.loads(function_call["arguments"]) if function_call["arguments"] else {}
        except json.JSONDecodeError:
            args = {}

        result = None
        for result_prototype in tool_handler(function_call["name"], args):
            result_prototype = json.loads(result_prototype)
            yield f"[TOOL_USE]{{\"tool_name\": \"{function_call['name']}\", \"query\": \"{args}\", \"tool_result\": \"{result_prototype['result']}\", \"is_open\": {json.dumps(result_prototype['done'])}}}[/TOOL_USE]\n\n"
            result = result_prototype['result']

        if result:
            messages.append({"role": "assistant", "content": f"{function_call['name']} with arguments {args}"})
            messages.append({"role": "user", "content": result})
            for chunk in cohere_complete(model, messages, images, max_tokens, system_prompt, tools):
                yield chunk
