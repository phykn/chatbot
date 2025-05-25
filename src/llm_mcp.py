from functools import partial

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

from fastmcp import Client
from fastmcp.client.transports import SSETransport

from .config import cfg_llm, cfg_mcp
from .misc import exists


def build_mcp_url(host: str, port: int, transport: str) -> str:
    return f"http://{host}:{port}/{transport}"


async def run_tool(name: str, arguments: dict):
    transport = SSETransport(url=build_mcp_url(**cfg_mcp["server"]))
    async with Client(transport) as client:
        outputs = await client.call_tool(name=name, arguments=arguments)
    return outputs[0]


async def init_astream():
    connection = {
        "url": build_mcp_url(**cfg_mcp["server"]), 
        "transport": cfg_mcp["server"]["transport"]
    }

    mcp = MultiServerMCPClient({"mcp": connection})
    tools = await mcp.get_tools()

    llm = ChatOpenAI(**cfg_llm["server"])
    llm_tool = llm.bind_tools(tools)

    llm_astream = partial(llm.astream, stop=cfg_llm["stop"])
    llm_tool_astream = partial(llm_tool.astream, stop=cfg_llm["stop"])

    return llm_astream, llm_tool_astream


class StreamHandler:
    def __init__(self):
        self.content = ""
        self.tool_calls = []
        self.tokens = []
        self.memory = {}

    @staticmethod
    def parse_tool(tool_call):
        return {
            "index": tool_call.get("index"),
            "id": tool_call.get("id"),
            "arguments": tool_call.get("function", {}).get("arguments"),
            "name": tool_call.get("function", {}).get("name"),
            "type": tool_call.get("type")
        }    
    
    def _update_content(self, chunk):
        if hasattr(chunk, "content") and exists(chunk.content):
            self.tokens.append(chunk.content)
            self.content = "".join(self.tokens)

    def _create_tool_call(self, index):
        self.memory[index] = {
            "index": None,
            "id": None,
            "function": dict(arguments="", name=""),
            "type": None
        }

    def _update_tool_call(self, data, index):
        if exists(data["index"]):
            self.memory[index]["index"] = data["index"]
        if exists(data["id"]):
            self.memory[index]["id"] = data["id"]
        if exists(data["arguments"]):
            self.memory[index]["function"]["arguments"] += data["arguments"]
        if exists(data["name"]):
            self.memory[index]["function"]["name"] = data["name"]
        if exists(data["type"]):
            self.memory[index]["type"] = data["type"]

    def update(self, chunk):
        self._update_content(chunk)

        if not hasattr(chunk, "additional_kwargs"):
            return
        
        chunk_tool_calls = chunk.additional_kwargs.get("tool_calls")
        if not exists(chunk_tool_calls):
            return
        
        for tool_call in chunk_tool_calls:
            data = self.parse_tool(tool_call)

            index = data["index"]
            if exists(index):
                if index not in self.memory:
                    self._create_tool_call(index)
                self._update_tool_call(data, index)

        self.tool_calls = list(self.memory.values())

    def __call__(self):
        return {"content": self.content, "tool_calls": self.tool_calls}
    

async def parse_astream(astream, messages):
    handler = StreamHandler()
    async for chunk in astream(messages):
        handler.update(chunk)
        yield handler()