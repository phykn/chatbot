import argparse
from fastmcp import FastMCP
from src.search import ddg_search
from src.misc import obj_to_str


def create_parser():
    parser = argparse.ArgumentParser(description="FastMCP Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8002, help="Server port")
    parser.add_argument("--transport", default="sse", help="Transport method")
    return parser


mcp = FastMCP("MCP Server")


@mcp.tool()
async def web_search(keyword: str, purpose: str = "") -> str:
    """Search the web for current information and recent updates.
    
    Args:
        keyword (str): Search terms or query to find relevant information
        purpose (str, optional): Context or intent of the search to improve result relevance
    
    Returns:
        str: Search results content including article text and relevant information
    """

    content = ddg_search(
        keywords = keyword,
        region = "wt-wt",
        max_results = 10,
        num_token_page = 2000,
        num_token_limit = 8000
    )

    output = {
        "keyword": keyword,
        "purpose": purpose,
        "content": content
    }
    
    return obj_to_str(output)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    mcp.run(
        host=args.host,
        port=args.port,
        transport=args.transport
    )
