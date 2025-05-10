import json


def exists(x):
    return x is not None


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def obj_to_str(obj):
    return json.dumps(obj, ensure_ascii=False)