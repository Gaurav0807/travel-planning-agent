import asyncio
from fastmcp import Client

WEATHER_MCP = "http://localhost:8001/sse"


def call_weather_tool(tool_name, args):
    return asyncio.run(_call_tool(tool_name, args))


async def _call_tool(tool_name, args):
    """Async call to MCP server"""
    async with Client(WEATHER_MCP) as client:
        result = await client.call_tool(tool_name, args)
        return result.content[0].text