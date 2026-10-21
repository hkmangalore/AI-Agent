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

load_dotenv()

llm_client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)


def format_answer(state):
    prompt = f"""
    The user asked:
    {state["user_request"]}
    Action Performed:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Answer the user naturally
    Do not mention internal planning.
    Do not mention state
    Do not mention tools.
    """
    response = llm_client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role":"system",
                "content":"You are a helpful assistant."
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()


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
