from typing import List, Dict, Tuple
from copy import deepcopy
from gradio import ChatMessage
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from .config import tokenizer, cfg_llm
from .misc import hash


class MessageCollector:
    def __init__(self):
        self.messages = dict(think_1=[], think_2=[], tool=[], ai=[])

    def update(self, messages: List[ChatMessage], mtype: str = "ai"):
        self.messages[mtype] = messages

    def check_tool(self) -> bool:
        return len(self.messages["tool"]) > 0

    def __call__(self, history: List[ChatMessage]) -> List[ChatMessage]:
        history = deepcopy(history)
        for msg_type in ["think_1", "tool", "think_2", "ai"]:
            history.extend(self.messages[msg_type])
        return history
    

def history_to_langchain(history: List[Dict[str, str]]) -> List[BaseMessage]:
    lc_history = []

    for message in history:
        if message["role"] == "user":
            lc_history.append(HumanMessage(message["content"]))
        elif message["role"] == "assistant":
            lc_history.append(AIMessage(message["content"]))
    
    return lc_history


def slice_messages(
    messages: List[BaseMessage],
    chat_info: Dict[str, int]
) -> Tuple[List[BaseMessage], List[BaseMessage], Dict[str, int]]:
    """Slice messages to fit within token limit while preserving system message."""
    
    if not messages:
        return messages
    
    # split messages
    system_messages, chat_messages = [], []
    for message in messages:
        if message.type == "system":
            system_messages.append(message)
        else:
            chat_messages.append(message)

    # system messages
    system_tokens = []
    for message in system_messages:
        content = message.content
        key = hash(content)

        if key not in chat_info:
            tokens = len(tokenizer.encode(content))
            chat_info[key] = tokens
        else:
            tokens = chat_info[key]

        system_tokens.append(tokens)
    system_tokens = sum(system_tokens)

    # get allow tokens
    max_input_tokens = cfg_llm["max_input_tokens"]
    allow_tokens = max_input_tokens - system_tokens
    
    # chat messages
    total_tokens = 0
    selected_messages = []    

    for i in range(len(chat_messages) - 1, -1, -1):
        message = chat_messages[i]

        content = message.content
        key = hash(content)

        if key not in chat_info:
            tokens = len(tokenizer.encode(content))
            chat_info[key] = tokens
        else:
            tokens = chat_info[key]

        total_tokens += tokens

        if total_tokens > allow_tokens:
            break

        selected_messages.append(chat_messages[i])

    selected_messages.reverse()
    return system_messages, selected_messages, chat_info