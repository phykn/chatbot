import argparse
from fastmcp import FastMCP
from src.search import ddg_search
from src.misc import obj_to_str, load_yaml


def create_parser():
    parser = argparse.ArgumentParser(description="FastMCP Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8002, help="Server port")
    parser.add_argument("--transport", default="sse", help="Transport method")
    return parser


mcp = FastMCP("MCP Server")
cfg = load_yaml("src/config.yaml")


@mcp.tool()
async def web_search(keyword: str, purpose: str) -> str:
    """Search web for current information beyond training data.

    Args:
        keyword (str): Search query terms
        purpose (str): Search intent for better filtering

    Returns:
        str: Relevant search results content
    """

    try:
        return obj_to_str({
            "keyword": keyword,
            "purpose": purpose,
            "content": ddg_search(keyword, **cfg["web_search"])
        })
    
    except:
        return "Not available"


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    mcp.run(
        host=args.host,
        port=args.port,
        transport=args.transport
    )
