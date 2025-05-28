from uuid import uuid4
from fastmcp import Client
from fastmcp.client.transports import SSETransport
from langchain_core.messages import SystemMessage, ToolMessage

from .config import cfg_mcp
from .message import parse_astream
from .qwen import parse_qwen3_text
from .misc import build_mcp_url


async def run_tool(name: str, arguments: dict):
    transport = SSETransport(url=build_mcp_url(**cfg_mcp["server"]))
    async with Client(transport) as client:
        outputs = await client.call_tool(name=name, arguments=arguments)
    return outputs[0]


async def stream_summary(
        llm_astream, 
        text: str, 
        summary_words: int = 300
    ):  

    tool_message = ToolMessage(content=text, tool_call_id=uuid4())
    
    system_prompt = f"""Analyze the provided content focusing on keywords: "{'keyword'}" and purpose: "{'purpose'}".
    Extract key information that directly relates to these keywords and serves the stated purpose.
    Summarize the most relevant points in {summary_words} words or less.
    Respond in the same language as the input content. /no_think"""

    system_message = SystemMessage(system_prompt)

    messages = [tool_message, system_message]
    async for data in parse_astream(llm_astream, messages):
        _, text = parse_qwen3_text(data["content"])
        yield text