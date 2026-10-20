from openai import OpenAI
from dotenv import load_dotenv
import os
print("my first program.........0")

# Load configuration from the .env file
load_dotenv()
print("my first program.........1")
# Create a client that communicates with Ollama
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
print("my first program.........2  Enter your input")

question = input("\nEnter your question : ")
print("my first program.........2.1 --> The question typed - " + question)
# Send a question to the AI model
response = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[
        {
            "role": "user",
            "content": question
            #"content": "What is Artificial Intelligence?"
        }
    ]
)
print("my first program.........3")
# Display the response
print(response.choices[0].message.content)
print("my first program.........4")
