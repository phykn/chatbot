import json
import yaml
from uuid import uuid4


class State:
    def __init__(self):
        self.value = uuid4()


def update_state(state):
    state.value = uuid4()


def exists(x):
    return x is not None


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_text(path):
    with open(path, "r", encoding='utf-8') as f:
        return f.read()


def obj_to_str(obj):      
    return json.dumps(obj, ensure_ascii=False)


def str_to_obj(text):
    return json.loads(text)


def build_mcp_url(host: str, port: int, transport: str) -> str:
    return f"http://{host}:{port}/{transport}"