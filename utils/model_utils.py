import json

with open("krypton_storage/models.json", "r") as file:
    models = json.load(file)

def get_model(model):
    model = models[model[2]][model[0]][model[1]]["name"]
    return model

def get_model_info(model):
    model_info = models[model[2]][model[0]][model[1]]
    return model_info

def get_model_path(model):
    model_path = get_model_info(model)["path"]
    return model_path

def get_model_family_info(api, product_family):
    product_family_info = models[api][product_family]
    return product_family_info

def is_local_model(api, product_family, model_version=None):
    # Check if the API is 'local'. If so, no need to verify model_version for local models.
    if api == 'Local':
        return product_family in models[api]
    elif model_version:
        # For non-local models, we also check if the model_version is specified correctly.
        return model_version in models[api][product_family]
    else:
        return False

