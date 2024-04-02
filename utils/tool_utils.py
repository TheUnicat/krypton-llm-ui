import json
tool_path = "krypton_storage/tools.json"
tool_settings_path = "krypton_storage/tool_settings.json"

from concurrent.futures import ThreadPoolExecutor
import asyncio
import threading


# Define a function to run the event loop
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


# Adjusted run_async to ensure the event loop runs
def run_async(func, *args):
    # Create a new event loop
    new_loop = asyncio.new_event_loop()

    # Start the new event loop in a separate thread
    t = threading.Thread(target=start_loop, args=(new_loop,))
    t.start()

    # Now we can safely run the coroutine in the new event loop
    future = asyncio.run_coroutine_threadsafe(func(*args), new_loop)
    return future  # Returns immediately; does not wait for future completion


def get_tools():
    with open(tool_path, "r") as file:
        tools = json.load(file)
    return list(tools.keys())


def clean_up_function_list(function_list):
    print(function_list)
    cleaned_list = []
    for item in function_list:
            print(item)
            cleaned_list.append(function_list[item])
    print("cleaned_list", cleaned_list)
    return cleaned_list

def get_tool_info(tool_name):
    with open(tool_path, "r") as file:
        tools = json.load(file)
    return clean_up_function_list(tools[tool_name])

def is_tool_enabled(tool_name):
    with open(tool_settings_path, "r") as file:
        tool_settings = json.load(file)
    return tool_settings.get(tool_name, False)

def get_enabled_tools():
    with open(tool_settings_path, "r") as file:
        tool_settings = json.load(file)
    enabled_tools = [tool for tool, enabled in tool_settings.items() if enabled]
    return enabled_tools