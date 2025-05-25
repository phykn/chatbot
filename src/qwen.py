import re
from typing import Tuple, List
from gradio import ChatMessage
from langchain_core.messages import SystemMessage, HumanMessage
from .llm_mcp import parse_astream
from .config import encoding


def parse_qwen3_text(
    text: str
) -> Tuple[str, str]:
    """Extracts text1 (from <think> block) and text2 (subsequent text) from Qwen3-like output."""

    text = text.strip()

    full_pattern = r"(?s)<think>(.*?)(?:</think>|/tool_call>)(.*)"
    match_full = re.search(full_pattern, text)

    if match_full:
        text1 = match_full.group(1).strip()
        text2 = match_full.group(2).strip()
        return text1, text2

    think_open_tag = "<think>"
    if text.startswith(think_open_tag):
        text1 = text[len(think_open_tag):].strip()
        text2 = ""
        return text1, text2
    else:
        text1 = ""
        text2 = text
        return text1, text2
    

def create_qwen3_chat_messages(
    text: str,
    think_title: str = "Thinking",
    think_status: str = "done"
) -> Tuple[List[ChatMessage], List[ChatMessage]]:
    """Parses Qwen3 text and creates ChatMessage lists for thought and AI response."""
    assert think_status in ["pending", "done"]
    
    text1, text2 = parse_qwen3_text(text)

    tool_messages = [] if not text1 else [ChatMessage(
        role = "assistant",
        content = text1,
        metadata = {"title": think_title, "status": think_status}
    )]

    ai_messages = [] if not text2 else [ChatMessage(
        role = "assistant",
        content = text2,
        metadata = None
    )]

    return tool_messages, ai_messages


def create_qwen3_tool_messages(
    tool_calls: List[dict],
    tool_status: str = "done"
) -> List[ChatMessage]:
    """Creates a list of ChatMessage objects from Qwen3 tool_calls with specified status."""
    assert tool_status in ["pending", "done"]

    tool_messages = []

    for tool_call in tool_calls:
        name = tool_call.get("function", {}).get("name")
        arguments = tool_call.get("function", {}).get("arguments")
        title = f"{name}: {arguments}"

        tool_message = ChatMessage(
            role = "assistant", 
            content = "",
            metadata = {"title": title, "status": tool_status}
        )
        tool_messages.append(tool_message)

    return tool_messages


async def stream_summary(
        llm_astream, 
        text: str, 
        max_tokens: int = 2048, 
        summary_words: int = 300
    ):

    tokens = encoding.encode(text)

    if len(tokens) < max_tokens:
        yield encoding.decode(tokens)
        return
    
    system_prompt = f"""Analyze the following text to identify its most critical information and key arguments. 
    Then, deliver a summary of these points in {summary_words} words or less.
    Please respond in the same language as the input text."""
    
    content = f"{encoding.decode(tokens[:max_tokens])} /no_think"

    messages = [SystemMessage(system_prompt), HumanMessage(content)]
    async for data in parse_astream(llm_astream, messages):
        _, text = parse_qwen3_text(data["content"])
        yield text