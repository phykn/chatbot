import json
import yaml


def exists(x):
    return x is not None


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def obj_to_str(obj):
    return json.dumps(obj, ensure_ascii=False)