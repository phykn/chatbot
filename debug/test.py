import asyncio
from fastmcp import Client
from fastmcp.client.transports import SSETransport

async def main():
    # 서버와 동일한 주소/포트, SSE 경로 사용
    transport = SSETransport(url="http://localhost:8082/sse")
    async with Client(transport) as client:
        tools = await client.list_tools()
        print("=== MCP 서버 툴 목록 ===")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())