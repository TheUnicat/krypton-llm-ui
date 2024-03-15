import storage
import json


#if test is enabled use a lorem ipsum generator as AI
with open("krypton_storage/test_mode.json", "r") as file:
    test_mode = json.load(file)["test_mode"]
    print(test_mode)

with open("krypton_storage/models.json", "r") as file:
    models = json.load(file)

def get_model(model_name, model_version):
    model = models[model_name]["models"][model_version]["name"]
    return model

def get_model_info(model_name, model_version):
    model = models[model_name]["models"][model_version]
    return model

def get_model_path(model_name, model_version):
    model_path = models[model_name]["models"][model_version]["path"]
    return model_path

def get_model_family_info(model_name):
    model_family_info = models[model_name]
    return model_family_info


def is_local_model(model_name, model_version):
    # Open and read the models.json file
    with open('krypton_storage/models.json', 'r') as file:
        models_data = json.load(file)

    # Check if the specified model and version exist and if its API is set to 'local'
    if model_name in models_data and model_version in models_data[model_name]['models']:
        return models_data[model_name]['api'] == 'local'
    else:
        return False

