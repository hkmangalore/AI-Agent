import tools
import tool_manager
from tool_manager import execute_tool
from tools import (get_current_time, roll_dice, generate_password, read_text_file)
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
print("      My AI Assistant Day 05")
print("=" * 40)

messages = [] 
roles = {
    "1": "You are a friendly school teacher. Explain every concept using simple language and real-life examples.",

    "2": "You are a senior Python developer. Explain programming concepts clearly and always include Python examples.",

    "3": "You are an experienced travel guide. Recommend places, food, transportation and travel tips.",

    "4": "You are a motivational coach. Encourage the user and give practical advice with a positive attitude.",

    "5": "You are a Technical coach. Provide technical guidance and support.",

    "6": "You are a professional interviewer. Ask one interview question at a time and provide feedback after each answer."
    
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

    user_input = input("\n Type your question  : ")

    
    ################################################################################################################
    #Before sending user input to AI, check if the request need to go to AI model or our built in tools
    tool_result = execute_tool(user_input) 
    
    if tool_result is not None:
        print("\nAI :", tool_result)
        continue

  ################################################################################################################      

    if user_input.lower().startswith("summarize "):
        
        print("\n..................    14 : ")
        
        # Extract the filename from the user input
        filename = user_input[10:].strip()
        print("\n..................    14..1 File name is  : "+filename)
        file_content = read_text_file("data/" + filename)
        print("\n..................    14..2 file_content  : "+file_content)
        prompt = f"""
        Summarize the following document.
        Document:
        {file_content}
        """
        user_input = prompt.strip()

        print("\n..................    14..3 user_input  : "+user_input)

        #continue    


    if user_input.lower().startswith("ask "):
        
        print("\n..................    14.......11 : ")
        
        parts = user_input.split(maxsplit=2)

        print(parts)
        filename = parts[1].strip()
        print("\n..................    14.......13 File name is  : "+filename)
        question = parts[2].strip()
        print("\n..................    14.......14 question is  : "+question)

        
        file_content = read_text_file("data/" + filename)
        print("\n..................    14.....14 ...  file_content  : "+file_content)
        prompt = f"""
        You are given a document.

        Answer the user's question based on the content of the document. If the answer is not present in the document, respond with "I couldn't find the information in the document".

        Document:
        {file_content}

        Question:
        {question}
        """
        user_input = prompt.strip()

        print("\n..................    14..14..... user_input(promt)  : "+user_input)

        #continue 

   ################################################################################################################       
    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    messages.append({
                "role": "user",
                "content": user_input 
                })
    print("\nSending the input to LLM ")
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

