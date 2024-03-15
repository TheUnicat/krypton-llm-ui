import json

def get_test_mode():
    #if test is enabled use a lorem ipsum generator as AI
    with open("krypton_storage/test_mode.json", "r") as file:
        test_mode = json.load(file)["test_mode"]

    return test_mode