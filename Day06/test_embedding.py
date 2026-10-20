from openai import OpenAI
from similarity import cosine_similarity

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    timeout=30,
)

response = client.embeddings.create(
    model="nomic-embed-text",
    input="Phython is programming language"
)

embedding = response.data[0].embedding
print("=" * 40)
print(" Embedding ------------1 \n")
print("Embedding vector length: --> ", len(embedding))
print("Embedding type: -->", type(embedding))
print("Embedding vector -->:", embedding)


response = client.embeddings.create(
    model="nomic-embed-text",
    #input="Phython is used for software development"
    input="Harish is from Bangalore and he is working as a software engineer. He is working on a project which is related to AI and ML. He is using Phython for software development."
)

embedding1 = response.data[0].embedding
print("=" * 40)
print(" Embedding ------------2 \n")
print("Embedding vector length: --> ", len(embedding1))
print("Embedding type: -->", type(embedding1))
print("Embedding vector -->:", embedding1)

print("\nCosine Similarity: -->", cosine_similarity(embedding, embedding1))



def create_embedding(content):
    embedding1 = client.embeddings.create(
    model="nomic-embed-text",
    input=content
    ).data[0].embedding
    return embedding1

    