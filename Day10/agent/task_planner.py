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
    You are an AI task planner. 
    Break the user's request into smaller tasks.
    Rules:
    1. Create only necessary tasks.
    2. Put tasks in execution order.
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

    print("decompose_task --> - Reponse from LLM :--> \n", response)

    result = response.choices[0].message.content.strip()
    tasks = []
    for line in result.splitlines():
        line = line.strip()
        if line:
            tasks.append(line)
            
    return tasks
