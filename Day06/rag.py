from openai import OpenAI
from dotenv import load_dotenv
import os
from retriever import load_documents

from rag_embedding import create_embedding

from similarity import cosine_similarity

documents = load_documents()

document_embeddings = {}

for filename, content in documents.items():

    document_embeddings[filename] = create_embedding(
        content
    )

# Load configuration
load_dotenv()

# Create AI client
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

print("=" * 80)
print("      My AI Assistant")
print("=" * 80)

messages =  []
# AI should know how to behave. Below line say's what system you want?
messages.append({
            "role": "system",
            "content": "Get the information from the document and answer the question. If the answer is not present in the document, respond with 'I couldn't find the information in the document'."
            })
            
while True:

    user_input = input("\nYou : ")

    if user_input.lower() == "quit":
        print("\nAI  : Goodbye! Have a great day.")
        break

    question_embedding = create_embedding(user_input)

    best_score = -1

    best_document = None

    for filename, embedding in document_embeddings.items():

        score = cosine_similarity(
        question_embedding,
        embedding
        )

        print(f"Score for {filename} --> : {score}")

        if score > best_score:
            best_score = score
            best_document = filename

    context = documents[best_document]

    prompt = f"""
        Answer the question using only
        the following information.

        Context:

        {context}

        Question:

        {user_input}
        """

    print("\nSending to LLM  :")

    
    # Add the prompt to the messages list
    messages.append({
                "role": "user",
                "content": prompt
                })
    
    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=messages
    )

    print("\nAI Result --> :", response.choices[0].message.content)

