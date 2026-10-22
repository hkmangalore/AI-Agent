import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def extract_memory(user_message, assistant_message):
    prompt = f"""
    You are a memory extractor system.

    Read the conversation below and determine 
    whether
    it contains useful log-term information about the user.

    User:
    {user_message}
    Assistant:
    {assistant_message}
    Store information only if it will be useful in future conversations.
    Useful informaiton includes:
    - preferences
    - interests
    - goals
    - skills
    - projects
    - important user facts
    Do NOT store:
    - temporary questions
    - current time
    - random calculations
    - one-time requests
    - tool results
    - casual conversation
    if useful information exists, 
    return ONLY the fact that should be remembered

    if there is nothing useful to remember, 
    return:NONE
    """
    response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    return response.choices[0].message.content.strip()
    