import re
import tiktoken
from copy import deepcopy
from .chat import stream_chat, stream_parse
from .config import model_table
from .misc import exists, load_json, obj_to_str


encoding = tiktoken.get_encoding("cl100k_base")


def del_think(text):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def user(history, content):
    if content.strip() != "":
        history = history + [{"role": "user", "content": content}]
    return history, ""


def assistant(history, option, state):
    init_id = None
    if not exists(init_id):
        init_id = state.msg_id

    if len(history) == 0:
        return history
    
    # option
    url = option["url"]
    model_name = option["model"]
    model = model_table[model_name]["name"]
    extensions = model_table[model_name]["extensions"]
    is_think = model_table[model_name]["is_think"]

    max_tokens = option["max_token"]
    do_think = option["do_think"]

    # system prompt
    system_prompt = load_json(f"src/prompts/core.json")
    for extension in extensions:
        extension = load_json(f"src/prompts/{extension}.json")
        system_prompt["extensions"].append(extension)
    system_prompt = obj_to_str(system_prompt)
    
    # slice messages
    messages = deepcopy(history)[::-1]
    system_token_num = len(encoding.encode(system_prompt))
    chat_token_nums = [len(encoding.encode(message["content"])) for message in messages]
    
    allow_tokens = max_tokens - system_token_num - 4
    total_tokens = 0

    sliced_messages = []
    for n, message in zip(chat_token_nums, messages):
        total_tokens += n
        if total_tokens > allow_tokens:
            break
        sliced_messages.append(message)

    messages = [{"role": "system", "content": system_prompt}] + sliced_messages[::-1]

    # add "/think" or "/no_think"
    if exists(do_think):
        user_message = messages[-1]
        if user_message["role"] == "user":
            appendix = f" /think" if do_think else f" /no_think"
            user_message["content"] = user_message["content"] + appendix
            messages[-1] = user_message

    # inference
    stream = stream_chat(
        url = url,
        model = model,
        messages = messages,
        options = {"num_ctx": max_tokens}
    )

    history = history + [{"role": "assistant", "content": ""}]

    for token in stream_parse(stream):
        if init_id != state.msg_id:
            break
        
        history[-1]["content"] = history[-1]["content"] + token
        yield history
    
    # del think tag
    if is_think:
        assistent_message = history[-1]
        if assistent_message["role"] == "assistant":
            assistent_message["content"] = del_think(assistent_message["content"])
        history[-1] = assistent_message
        yield history

    return history