import json
import yaml


def obj_to_str(obj):      
    return json.dumps(obj, ensure_ascii=False)


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)