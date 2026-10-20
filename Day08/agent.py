from openai import OpenAI
#from mcp import MCPServer
from dotenv import load_dotenv
import os
import asyncio

from mcp_client import connect, discover_tools, execute_tool, disconnect, execute_tool


#Our Ai agent will perform 6 steps
#1. Connect to the MCP server tool
#2. Discover available tools on the MCP server
#3. Give a tool description to Ollama model
#4. Ask Ollama to choose a right tool
#5. Execute the chosen tool with the provided arguments through the MCP client
#6. Generate a natural language response based on the tool's output
#7. Disconnect from the MCP server tool

#Note:
    # For open AI --> run this --> python -m pip install openai

load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

 
async def main():
    #1. Connect to the MCP server tool
    client = await connect()

    #2. Discover available tools on the MCP server
    tools = await discover_tools(client)

    # print available tools
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")



    #3. Give a tool description to Ollama
    #4. Ask Ollama to choose a tool and provide arguments
    user_request=input("User:")
    tool_name=planner(user_request, tools)

    print()
    print("Planner Selected (i.e LLM)-->:", tool_name)

    #5. Execute the chosen tool with the provided arguments
    result = await execute_tool(client, tool_name)
    
    #6. Generate a natural language response based on the tool's output
    final_answer = generate_response(user_request, result)
    print("\n\n Final LLM Response: --->  "+final_answer)

    # Disconnect from the MCP server
    await disconnect(client)

def planner(user_request, tools):
    prompt = build_tool_description(tools, user_request)
    
    response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()

def generate_response(user_request, tool_request):
    prompt = f"""
             The user asked: {user_request}   
             The tool returned: {tool_request}
             Answer naturally.
            """
    response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[
                       {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()

def build_tool_description(tools, user_request):
    """Build a description of the tool for the AI agent."""
    tool_description = ""
    for tool in tools:
        tool_description += f"""Tool:{tool.name}: Description:{tool.description} """
    
    prompt = f"""
            You are an AI planner.
            Available tools:
            {tool_description}
            Instruction
            1. Select the best tool
            2. Reply ONLY with the tool name
            3. Do not explain
            User Request
            {user_request}
        """
    print("LLM prompt: "+ prompt)
    return prompt

#check if this file being run directly.
if __name__ == "__main__":
    #start the asynchronous function
    asyncio.run(main())
