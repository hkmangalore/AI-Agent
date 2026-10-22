import json
#Python can directly work with SQLite
import sqlite3
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os
DATABASE = "memory.db"

load_dotenv()

# Create AI client
embedding_client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def create_database():
    connection= sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT,
        assistant_message TEXT,
        embedding TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    connection.commit()
    connection.close()


def create_embedding(text):
    response = embedding_client.embeddings.create(
        model="nomic-embed-text",
        input=text
    )

    return response.data[0].embedding

def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    return np.dot(v1, v2)/(np.linalg.norm(v1) * np.linalg.norm(v2) )

def save_memory(user_message, assistant_message):
    text = user_message + "\n" + assistant_message
    print("save_memory --> text = \n ", text)
    embedding = create_embedding(text)
    connection= sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories
        (
        user_message, assistant_message, embedding
        )
        VALUES (?,?,?)
        """, 
        (
            user_message, assistant_message, json.dumps(embedding)
        )
    )
    connection.commit()
    connection.close()


def save_semantic_memory(fact):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    embedding = create_embedding(fact)  

    cursor.execute("""
            INSERT INTO memories(
            user_message,
            assistant_message,
            embedding
            )
            VALUES(?,?,?)
        """,
        fact,"", json.dumps(embedding)
        )
    connection.commit()
    connection.close()

def search_semantic_memories(query, top_k=3, threshold=0.2):
    query_embeddings = create_embedding(query)
    connection= sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    query = f"""
        SELECT
        user_message ,
        assistant_message ,
        embedding ,
        created_at
        FROM memories
        """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    connection.close()

    results = []

    for (
        user_message ,
        assistant_message ,
        embedding_json ,
        created_at
        ) in rows:
        memory_embedding=json.loads(embedding_json)

    score = cosine_similarity(query_embeddings, memory_embedding)

    if score >= threshold:
        results.append({
                "user_message": user_message,
                "assistant_message": assistant_message,
                "created_at": created_at,
                "score": score
        })

        results.sort(key=lambda item:item["score"], reverse=True)
    return results[:top_k]