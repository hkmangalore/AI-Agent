"""
Plan the next action for the AI agent using an OpenAI-compatible chat model.

The module loads configuration from environment variables and creates a client.
`build_tool_description` is intended to format available tools for the model,
while `planner` combines those tools with the user's request and prior
observations, then returns the model's next tool name or `FINISH`.

The current implementation has issues that prevent this flow from working:
the dotenv import does not match the function called, and
`build_tool_description` uses an undefined variable and returns inside its
loop.
"""

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def build_tool_description(tools):
    description = ""
    for tool in tools:
        description += f"""
        Tool:
        {tool.name}
        Description:{tool.description}
        """

    return description


def planner(state, tools):
    """Ask the model to choose the next tool or finish the request.
    Uses the user's request, prior observations, and available tool descriptions
    to build a prompt. Returns the model's response with surrounding whitespace
    removed; the expected response is a tool name or ``FINISH``.
    """
    tool_descriptions = build_tool_description(tools)
    prompt = f"""
    You are an AI Planner
    Your job is to decide only the next action
    User Request:
    {state["user_request"]}
    Previous Observations:
    {state["observations"]}
    Available Tools:
    {tool_descriptions}
    Rules:
    1. Choose only from next action
    2. Never repeat an action that has already completed
    3. Use the observations to decide what is still require
    4. if the user's request has been completly satisfied, return FINISH.
    5. Return ONLY the tool name or FINISH.
    6. Do not explain your answer
    Next Action:
    """

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role":"system",
                "content":"You are an AI Planner."
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content.strip()
