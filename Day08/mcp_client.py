from fastmcp import Client

async def connect():
    """Connect to the MCP server tool."""

    client = Client("server.py")
    
    await client.__aenter__()
    print ("Connected to the MCP server tool.")
    return client


async def disconnect(client):
    """MCP Client -->>>Disconnect from the MCP server tool."""

    await client.__aexit__(None, None, None)
    print ("MCP Client -->>>Disconnected from the MCP server tool.")

async def discover_tools(client):
    """Discover available tools on the MCP server."""

    tools = await client.list_tools()
    print ("\n\n MCP Client -->>>Discovered tools:", tools)
    print("\n\n" + "=" * 80)
    return tools

async def execute_tool(client, tool_name, arguments=None):
    """Execute a tool on the MCP server.""" 
    print("........1..............")
    arguments = dict(arguments) if arguments is not None else {}
    print("........2.............. tool_name --> ", tool_name.name)      
    
    result = await client.call_tool(tool_name.name, arguments)
    print(f"\n\n MCP Client -->>>Executed tool '{tool_name}' with result:", result)
    return result