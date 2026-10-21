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
    """
    asks the configured chat model to decide what the agent should do next. It includes the user’s request, 
    current tasks, completed actions, observations, results, and available tool descriptions in its prompt. 
    The model is instructed to choose one pending task and a suitable tool, or return FINISH when all 
    tasks are complete. The function returns the model’s response as stripped text, 
    expected to follow the Task: ... and TOOL: ... format.

    Args:
        state: Agent state containing ``user_request``, ``tasks``, ``actions``,
            ``observations``, and ``results``.
        tools: Available tools, each with a ``name`` and ``description``.

    Returns:
        The model's decision as stripped text, expected to contain
        ``Task: <task>`` and ``TOOL: <tool>`` (or ``FINISH``).

    """
    tool_descriptions = build_tool_description(tools)
    prompt = f"""
    You are an AI Planner
    Your job is to select the next unfinished task and the best tool to complete it.
    User Request:
    {state["user_request"]}
    Tasks:
    {state["tasks"]}
    Pending Tasks:
    {[
        item["task"]
        for item in state["tasks"]
        if item["status"] == "pending"
    ]}
    Completed Actions:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Immediate Results:
    {state["results"]}
    Available Tools:
    {tool_descriptions}
    Rules:
        1. Select only ONE pending task.
        2. The TASK must be copied EXACTLY from the
        pending task list.
        3. Do not change the task wording.
        4. Do not select a completed task.
        5. Select the best available tool for that task.
        6. Use previous observations and results.
        7. If an action failed, reconsider the task.
        8. If there are no pending tasks,return ONLY the word: FINISH
        9. If tasks are still pending, return exactly
        two lines in this format:
            TASK: <exact pending task>
            TOOL: <tool_name>
        10. Do not explain anything.

    Next Decision:
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
