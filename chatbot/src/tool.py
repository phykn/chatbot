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
        max_len: int = 2000,
        summary_words: int = 500
    ):

    if len(text) < max_len:
        yield text
    
    else:
        tool_message = ToolMessage(content=text, tool_call_id=uuid4())
        
        system_prompt = f"""**Content Analysis:**
        - Focus on keywords: "{'keyword'}" and purpose: "{'purpose'}"
        - Extract directly relevant information
        
        **Preservation Guidelines:**
        - Maintain original wording and specific details
        - Prioritize accuracy over brevity
        - Retain essential context
        
        **Summary Requirements:**
        - Structure: Main topic → core points → key insight
        - Length: {summary_words} words or less
        - Match language and tone to audience /no_think"""

        system_message = SystemMessage(system_prompt)

        messages = [tool_message, system_message]
        async for data in parse_astream(llm_astream, messages):
            _, text = parse_qwen3_text(data["content"])
            yield text