from datetime import datetime
from functools import partial

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage
from .config import cfg_llm, cfg_mcp
from .misc import exists, load_text, build_mcp_url


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


def build_system_message(do_think=False) -> SystemMessage:
    main = load_text("src/prompt/main.txt")
    time = f"**Current Time:**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    extension_names = cfg_llm.get("extensions", [])
    extensions = [load_text(f"src/prompt/{name}.txt") for name in extension_names]

    mode = f"**Mode:**: {'/think' if do_think else '/no_think'}" 

    content = "\n\n".join([main, time] + extensions + [mode])
    return SystemMessage(content=content)


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