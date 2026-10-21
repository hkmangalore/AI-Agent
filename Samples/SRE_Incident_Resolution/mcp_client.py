import sys
import asyncio
from typing import Dict, Any
from contextlib import AsyncExitStack

# Google GenAI SDK
from google import genai
from google.genai import types

# MCP SDK
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SYSTEM_PROMPT = """You are "Relay", an expert SRE Incident Response AI Agent.

INVESTIGATION PROTOCOL (MANDATORY ORDER):
1. STARTING POINT (ServiceNow): Always query the ServiceNow incident ticket first using `get_servicenow_incident` to identify the failure description, priority, impacted configuration item (CI), and work notes.
2. JIRA CROSS-REFERENCE: Use `get_jira_issue` if the ServiceNow ticket references a Jira key or associated engineering bug ticket.
3. GIT CORRELATION: Use `search_recent_commits` to inspect recent code updates in the affected service repo within the incident timeframe.
4. DIFF ANALYSIS: Use `get_commit_diff` to review suspect code modifications.
5. SYNTHESIS: Deliver a concise root-cause analysis with actionable remediation steps.
"""

class GeminiMCPClient:
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.genai_client = genai.Client()
        self.exit_stack = AsyncExitStack()
        self.session: ClientSession = None

    async def connect_to_mcp_server(self):
        """Start the MCP Server process over stdio and initialize an MCP session."""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[self.server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read_stream, write_stream = stdio_transport
        
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self.session.initialize()
        print(" Connected to MCP Server successfully.")

    async def run_agent_loop(self, user_query: str):
        """Fetch MCP tools, map schemas, and handle LLM tool execution turns."""
        mcp_tools_list = await self.session.list_tools()
        
        gemini_function_declarations = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=tool.inputSchema
            )
            for tool in mcp_tools_list.tools
        ]

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.1,
            tools=[types.Tool(function_declarations=gemini_function_declarations)]
        )

        print(f"\n User Query: {user_query}\n" + "-"*50)

        response = self.genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_query,
            config=config
        )

        conversation_history = [user_query]

        while response.function_calls:
            for call in response.function_calls:
                tool_name = call.name
                tool_args = call.args

                print(f" LLM calling MCP Tool `{tool_name}` with arguments: {tool_args}")

                mcp_result = await self.session.call_tool(tool_name, arguments=tool_args)

                tool_content = [item.text for item in mcp_result.content if hasattr(item, "text")]
                output_str = "\n".join(tool_content)

                conversation_history.append(response.candidates[0].content)
                conversation_history.append(
                    types.Content(
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name,
                                response={"result": output_str}
                            )
                        ]
                    )
                )

            response = self.genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=conversation_history,
                config=config
            )

        print("\n Final Incident Synthesis:\n" + "="*50)
        print(response.text)

    async def close(self):
        await self.exit_stack.aclose()


async def main():
    client = GeminiMCPClient(server_script_path="server.py")
    try:
        await client.connect_to_mcp_server()
        # Starting investigation directly from ServiceNow incident ticket INC0010042
        await client.run_agent_loop(
            "ServiceNow incident INC0010042 just came in for a production checkout failure. "
            "Start the investigation from ServiceNow and trace down the root cause across connected tools."
        )
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())