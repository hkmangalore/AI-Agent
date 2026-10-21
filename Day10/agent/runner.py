import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from mcp_client import connect, disconnect, discover_tools
from agent.planner import planner
from agent.executor import execute_action
from agent.loop import run_agent_loop
from agent.answer import format_answer

load_dotenv()

llm_client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


async def main():
    mcp_client = await connect()
    try:
        tools = await discover_tools(mcp_client)

        print("\nAvailable Tools")
        print("==================")
        for tool in tools:
            print(tool.name)

        user_request = input("\nWrite your request here: ")
        state = await run_agent_loop(
            user_request,
            planner,
            execute_action,
            format_answer,
            tools,
            mcp_client,
        )

        print("\nFinal Answer:\n" + state["final_answer"])
    finally:
        await disconnect(mcp_client)


if __name__ == "__main__":
    asyncio.run(main())
