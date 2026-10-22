import asyncio

from memory import create_database

from mcp_client import (
    connect,
    disconnect,
    discover_tools
)

from planner import planner
from executor import execute_action
from loop import run_agent_loop
from answer import format_answer


async def main():

    create_database()
    client = await connect()

    tools = await discover_tools(
        client
    )

    print("\nAvailable Tools")
    print("----------------")

    for tool in tools:
        print(tool.name)

    user_request = input(
        "\nUser : "
    )

    state = await run_agent_loop(
        user_request,
        planner,#LLM call
        execute_action,#Toolcall
        format_answer,#LLM call
        tools,
        client
    )

    print("\nFinal Answer")
    print("------------")

    print(
        state["final_answer"]
    )

    await disconnect(client)


if __name__ == "__main__":
    asyncio.run(main())



