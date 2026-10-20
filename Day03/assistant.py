from openai import OpenAI
from dotenv import load_dotenv
import os

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

print("=" * 40)
print("      My AI Assistant Day 03")
print("=" * 40)

messages = [] 
roles = {
    "1": "You are a friendly school teacher. Explain every concept using simple language and real-life examples.",

    "2": "You are a senior Python developer. Explain programming concepts clearly and always include Python examples.",

    "3": "You are an experienced travel guide. Recommend places, food, transportation and travel tips.",

    "4": "You are a motivational coach. Encourage the user and give practical advice with a positive attitude.",

    "5": "You are a professional interviewer. Ask one interview question at a time and provide feedback after each answer."
}

print("\n Chose your system:")
for role in roles:
    print("\n " + role +" =    "  +roles[role])

#system_input = input("\n Enter what AI system  shold behave as ? (Teacher/Python Expert/Travel guid etc...) ")

system_input = input("\n Enter what AI system  shold behave as ? (type number) ")
print("\n I have selected a choise as : "+ system_input)

# AI should know how to behave. Below line say's what system you want?
messages.append({
                "role": "system",
                "content": roles.get(system_input, "You are a helpful AI assistant.")
                })
while True:

    user_input = input("\nYou : ")

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break
    messages.append({
                "role": "user",
                "content": user_input 
                })
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )
    ai_reply = response.choices[0].message.content
    print("\nAI :", ai_reply)
    messages.append({
        
        "role": "assistant",
        "content": ai_reply
        
       })

    print("\nList :", messages)

