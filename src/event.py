import re
import tiktoken
from typing import List
from copy import deepcopy
from .chat import stream_post, stream_parse
from .misc import exists, load_yaml, obj_to_str


encoding = tiktoken.get_encoding("cl100k_base")
cfg_front = load_yaml("src/config/front.yaml")
cfg_ollama = load_yaml("src/config/ollama.yaml")


def update_obj(obj: dict, key: str, value: any):
    obj[key] = value
    return obj


def user(history, content):
    if content.strip() != "":
        history = history + [{"role": "user", "content": content}]
    return history, ""


def get_system_prompt(extensions):
    system_prompt = load_yaml("src/system_prompt/core.yaml")

    for extension in extensions:
        extension = load_yaml(f"src/system_prompt/{extension}.yaml")
        system_prompt["extensions"].append(extension)

    return obj_to_str(system_prompt)


def slice_history(
    history: List[dict], 
    system_prompt: str,
    max_token: int
) -> List[dict]:
    
    messages = deepcopy(history)[::-1]
    system_token_num = len(encoding.encode(system_prompt))
    chat_token_nums = [len(encoding.encode(message["content"])) for message in messages]
    
    allow_tokens = max_token - system_token_num - 4
    total_tokens = 0

    sliced_messages = []
    for n, message in zip(chat_token_nums, messages):
        total_tokens += n
        if total_tokens > allow_tokens:
            break
        sliced_messages.append(message)

    return sliced_messages[::-1]


def add_think_tag(
    messages: List[dict], 
    do_think: bool = False
) -> List[dict]:   
    
    appendix = f" /think" if do_think else f" /no_think"

    message = messages[-1]
    message["content"] = message["content"] + appendix

    messages[-1] = message
    return messages


def del_think(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def del_think_tag(history):
    message = history[-1]
    message["content"] = del_think(message["content"])
    history[-1] = message
    return history


def assistant(history, option, uuid):
    ini_id = None
    if not exists(ini_id):
        ini_id = uuid.value

    if len(history) == 0:
        return history
    
    # option
    model_info = cfg_front["model"][option["model"]]

    # preprocess
    system_prompt = get_system_prompt(model_info["extensions"])
    sliced_messages = slice_history(history, system_prompt, option["max_token"])
    messages = [{"role": "system", "content": system_prompt}] + sliced_messages
    messages = add_think_tag(messages, option["do_think"])

    # inference
    stream = stream_post(
        url = cfg_ollama["url"],
        model = model_info["endpoint"],
        messages = messages,
        options = {
            "num_ctx": option["max_token"]
        }
    )

    # print
    history = history + [{"role": "assistant", "content": ""}]
    for token in stream_parse(stream):
        if ini_id != uuid.value:
            break

        history[-1]["content"] = history[-1]["content"] + token
        yield history
    
    # postprocess
    if model_info["is_think"]:
        yield del_think_tag(history)

    return history