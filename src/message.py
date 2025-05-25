from typing import Tuple, List, Dict
from copy import deepcopy
from datetime import datetime
from langchain_core.messages import (
    BaseMessage, 
    SystemMessage, 
    HumanMessage, 
    AIMessage
)

from .config import encoding, cfg_llm
from .misc import load_yaml, obj_to_str


def history_to_langchain(history: List[Dict[str, str]]) -> List[BaseMessage]:
    lc_history = []

    for message in history:
        if message["role"] == "user":
            lc_history.append(HumanMessage(message["content"]))
        elif message["role"] == "assistant":
            lc_history.append(AIMessage(message["content"]))
    
    return lc_history


def build_system_message() -> SystemMessage:
    content = load_yaml("src/prompt/core.yaml")

    # add current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content["extensions"].append({"current_time": current_time})

    # load and append configured extensions
    extension_names = cfg_llm.get("extensions", [])
    for name in extension_names:
        extension_content = load_yaml(f"src/prompt/{name}.yaml")
        content["extensions"].append(extension_content)

    return SystemMessage(content=obj_to_str(content))


def add_think_tag(
    messages: List[BaseMessage],
    do_think: bool = False
) -> List[BaseMessage]:
    
    if not messages:
        return messages
    
    messages = deepcopy(messages)
    text = "/think" if do_think else "/no_think"
    messages[-1].content = f"{messages[-1].content} {text}"
    return messages


def slice_messages(
    messages: List[BaseMessage],
    eps: int = 8
) -> Tuple[List[BaseMessage], List[BaseMessage]]:
    """Slice messages to fit within token limit while preserving system message."""
    
    if not messages:
        return messages
    
    system_messages = []
    chat_messages = []

    for message in messages:
        if message.type == "system":
            system_messages.append(message)
        else:
            chat_messages.append(message)

    system_tokens = sum([len(encoding.encode(m.content)) + eps for m in system_messages])

    max_input_tokens = cfg_llm["max_input_tokens"]
    allow_tokens = max_input_tokens - system_tokens
    
    selected_messages = []
    total_tokens = 0

    for i in range(len(chat_messages) - 1, -1, -1):
        message = chat_messages[i]
        chat_tokens = len(encoding.encode(message.content)) + eps
        total_tokens += chat_tokens
        
        if total_tokens > allow_tokens:
            break

        selected_messages.append(chat_messages[i])

    selected_messages.reverse()

    return system_messages, selected_messages