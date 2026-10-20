from retriever import load_documents
from retriever import retrieve

documents = load_documents()
for filename, content in documents.items():
    print(f"Filename: {filename}")
    print(f"Content: {content}")
    print("-" * 40)


question = "mySQL"
filename, content = retrieve(question)
print(f"Filename: {filename}")
print()
print(f"Content: {content}")