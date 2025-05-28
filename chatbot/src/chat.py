from typing import List, Dict, Tuple
from copy import deepcopy
from gradio import ChatMessage
from langchain_core.messages import (
    BaseMessage,
    HumanMessage, 
    AIMessage
)
from .config import tokenizer, cfg_llm


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

    system_tokens = sum([len(tokenizer.encode(m.content)) + eps for m in system_messages])

    max_input_tokens = cfg_llm["max_input_tokens"]
    allow_tokens = max_input_tokens - system_tokens
    
    selected_messages = []
    total_tokens = 0

    for i in range(len(chat_messages) - 1, -1, -1):
        message = chat_messages[i]
        chat_tokens = len(tokenizer.encode(message.content)) + eps
        total_tokens += chat_tokens
        
        if total_tokens > allow_tokens:
            break

        selected_messages.append(chat_messages[i])

    selected_messages.reverse()

    return selected_messages, system_messages