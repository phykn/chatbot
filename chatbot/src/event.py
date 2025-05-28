from uuid import uuid4
from typing import List, Tuple, AsyncGenerator
from gradio import ChatMessage
from langchain_core.messages import ToolMessage

from .chat import MessageCollector, history_to_langchain, slice_messages
from .message import init_astream, parse_astream, build_system_message
from .qwen import create_qwen3_chat_messages, create_qwen3_tool_messages
from .tool import run_tool, stream_summary
from .config import cfg_mcp
from .misc import str_to_obj, State


def add_user_message(
    chat_history: List[ChatMessage], 
    user_input: str
) -> Tuple[List[ChatMessage], str]:
    
    user_input = user_input.strip()

    if user_input == "":
        return chat_history, ""
    
    messages = [ChatMessage(
        role = "user", 
        content = user_input, 
        metadata = None
    )]

    return chat_history + messages, ""


async def add_ai_message(
    chat_history: List[ChatMessage], 
    do_think: bool, 
    state: State
) -> AsyncGenerator[List[ChatMessage], None]:

    if not chat_history:
        yield chat_history
        return

    # initialize
    init_state = state.value
    llm_astream, tool_astream = await init_astream()

    # prepare message
    system_message = build_system_message(do_think=do_think)
    chat_messages = [m for m in chat_history if m.get("metadata") is None]

    messages = history_to_langchain(chat_messages) + [system_message]
    chat_messages, system_messages = slice_messages(messages)
    messages = chat_messages + system_messages

    # tool_astream
    tool_calls = None
    collector = MessageCollector()

    async for data in parse_astream(tool_astream, messages):
        if init_state != state.value: break

        try:
            tool_calls = data["tool_calls"]

            think_messages, ai_messages = create_qwen3_chat_messages(
                text=data["content"], think_title="Thinking", think_status="pending"
            )
            tool_messages = create_qwen3_tool_messages(
                tool_calls=tool_calls, tool_status="pending"
            )

            collector.update(think_messages, mtype="think_1")
            collector.update(ai_messages, mtype="ai")
            collector.update(tool_messages, mtype="tool")
            yield collector(chat_history)

        except: break

    for message in collector.messages["think_1"]:
        message.metadata["status"] = "done"
    yield collector(chat_history)

    # llm_astream
    if collector.check_tool() and tool_calls:
        tool_messages = collector.messages["tool"]
        for tool_call, tool_message in zip(tool_calls, tool_messages):
            if init_state != state.value: break

            try:
                func = tool_call.get("function", {})
                tool_output = await run_tool(
                    name = func.get("name", ""),
                    arguments = str_to_obj(func.get("arguments", "{}"))
                )

                astream = stream_summary(llm_astream, tool_output.text, **cfg_mcp["summary"])
                async for text in astream:
                    if init_state != state.value: break
                    tool_message.content = text
                    yield collector(chat_history)

            except: continue

        for message in collector.messages["tool"]:
            message.metadata["status"] = "done"
        yield collector(chat_history)

        # answer
        messages.extend([ToolMessage(m.content, tool_call_id=uuid4()) for m in tool_messages])
        chat_messages, system_messages = slice_messages(messages)
        messages = chat_messages + system_messages

        async for data in parse_astream(llm_astream, messages):
            if init_state != state.value: break

            try:
                think_messages, ai_messages = create_qwen3_chat_messages(
                    text=data["content"], think_title="Thinking", think_status="pending"
                )

                collector.update(think_messages, mtype="think_2")
                collector.update(ai_messages, mtype="ai")
                yield collector(chat_history)

            except: break

        for message in collector.messages["think_2"]:
            message.metadata["status"] = "done"
        yield collector(chat_history)