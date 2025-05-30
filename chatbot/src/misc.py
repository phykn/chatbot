import json
import yaml
import hashlib
from typing import List
from uuid import uuid4
from datetime import datetime
from langchain_core.messages import SystemMessage


class State:
    def __init__(self):
        self.value = uuid4()


def update_state(state):
    state.value = uuid4()


def exists(x):
    return x is not None


def hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def build_system_message(
    do_think: bool = False, 
    extension_names: List[str] = []
) -> SystemMessage:
    
    main = load_text("src/prompt/main.txt")
    
    extensions = [load_text(f"src/prompt/{name}.txt") for name in extension_names]

    time = f"**Current Time:**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    mode = f"**Mode:**: {'/think' if do_think else '/no_think'}" 

    content = "\n\n".join([main] + extensions + [time, mode])
    return SystemMessage(content=content)