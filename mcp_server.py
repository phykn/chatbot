from fastmcp import FastMCP
from src.search import ddg_search
from src.config import cfg_web
from src.misc import load_yaml, obj_to_str


mcp = FastMCP("MCP Server")


@mcp.tool(
    name = "web_search",
    description = "Search the web for current information and recent updates",
    tags = {"internet", "web", "search", "information"}
)
async def web_search(keyword: str) -> str:
    data = ddg_search(keyword, **cfg_web["ddg"])
    return obj_to_str(data)


if __name__ == "__main__":
    cfg = load_yaml("src/config/mcp.yaml")
    mcp.run(**cfg["server"])