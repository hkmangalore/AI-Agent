from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def decompose_task(user_request):
    prompt = f"""
    You are an AI task planner. break the user request into smaller tasks.
    Rules:
    1. Create only the task neccessary to complete the request.
    2. Put the tasks in the correct execution order.
    3. Each task should be a short action.
    4. Return one task per line.
    5. Do  not number the tasks.
    6. Do not explaining anything.
    User Request:
    {user_request}
    """

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=[
            {
                "role":"system",
                "content":"You are an AI Task Planner."
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    result = response.choices[0].message.content.strip()
    tasks = []
    for line in result.splitlines():
        line = line.strip()
        if line:
            tasks.append(line)
            
    return tasks
