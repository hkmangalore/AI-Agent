from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def format_answer(state):
    prompt = f"""
    The user asked:
    {state["user_request"]}
    Tasks:
    {state["tasks"]}
    Actions:
    {state["actions"]}
    Observations:
    {state["observations"]}
    Intermediate Results:
    {state["results"]}
    Give the user a natural and concise answer
    Do not mention
    - planner
    - agent loop
    - MCP
    - internal state
    - tools
    - internal reasoning
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
