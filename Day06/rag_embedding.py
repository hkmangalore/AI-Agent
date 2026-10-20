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

def create_embedding(content):
    embedding1 = client.embeddings.create(
    model="nomic-embed-text",
    input=content
    ).data[0].embedding
    return embedding1