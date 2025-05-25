import json
import yaml


def exists(x):
    return x is not None


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise


def load_yaml(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError):
        raise


def obj_to_str(obj):      
    return json.dumps(obj, ensure_ascii=False)


def str_to_obj(text):
    return json.loads(text)