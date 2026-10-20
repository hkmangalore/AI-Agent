import asyncio

from mcp_client import *

async def main():
    # Connect to the MCP server
    client = await connect()

    # Discover available tools
    tools = await discover_tools(client)

    #print("Available tools on the MCP server:", tools)
    print("\n\n" + "=" * 80)

    for tool in tools:
        print(f"Executing tool: {tool} \n\n") 
        result = await execute_tool(client, tool.name)
        print(f"Result from tool '{tool}': {result}")
        print("=" * 80)    
        print("=" * 80)    
        
        print("\n\n  Result >>>>:", result.content[0].text)

    # Disconnect from the MCP server
    await disconnect(client)

asyncio.run(main())