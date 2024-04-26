import json
tool_path = "krypton_storage/tools.json"
tool_settings_path = "krypton_storage/tool_settings.json"

def get_tools():
    with open(tool_path, "r") as file:
        tools = json.load(file)
    return list(tools.keys())

def toggle_tool_status(tool_name):
    with open(tool_settings_path, "r") as file:
        tool_settings = json.load(file)
    tool_settings[tool_name] = not tool_settings.get(tool_name, False)
    with open(tool_settings_path, "w") as file:
        json.dump(tool_settings, file, indent=4)

def clean_up_function_list(function_list):
    cleaned_list = []
    for item in function_list:
            cleaned_list.append(item)
    return cleaned_list

def get_tool_info(tool_name):
    with open(tool_path, "r") as file:
        tools = json.load(file)
    return tools[tool_name]

def is_tool_enabled(tool_name):
    with open(tool_settings_path, "r") as file:
        tool_settings = json.load(file)
    return tool_settings.get(tool_name, False)

def get_enabled_tools():
    with open(tool_settings_path, "r") as file:
        tool_settings = json.load(file)
    enabled_tools = [tool for tool, enabled in tool_settings.items() if enabled]
    return enabled_tools


def format_tool_info(tool):
    # Extract the description of the tool
    description = tool["function"]["description"]

    # Prepare a list to hold parameters' details
    parameters = []

    # Iterate through the properties of the parameters to get each parameter's details
    for param_name, param_info in tool["function"]["parameters"]["properties"].items():
        # Check if the parameter is required
        is_required = param_name in tool["function"]["parameters"]["required"]

        # Append the parameter's details as a dictionary to the parameters list
        parameters.append({
            "name": param_name,
            "type": param_info["type"],
            "description": param_info["description"],
            "required": is_required
        })

    # Form the output JSON
    formatted_info = {
        "description": description,
        "parameters": parameters
    }

    return formatted_info

#retrieves tool info and returns formatted tool info from tool name
def get_formatted_tool_info(tool_name):
    tool = get_tool_info(tool_name)
    return format_tool_info(tool)