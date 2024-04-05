from tools.search_tool import google


def tool_handler(name, arguments):
    """
    Calls the function identified by 'name' with 'arguments' and returns the output.

    :param name: String, the name of the function to call.
    :param arguments: The arguments to pass to the function.
    :return: The output of the function call.
    """
    # Attempt to retrieve the function by name from the global scope
    func = globals().get(name)

    # If the function exists, call it with the provided arguments
    if func:
        return func(arguments)
    else:
        raise ValueError(f"No function named '{name}' found.")
