from pathlib import Path

# load documents from knowledge folder ending with .txt and return as documents dictionary with filename as key and content as value
def load_documents():
    documents = {}
    folder = Path("knowledge")
    for file in folder.glob("*.txt"):
        documents[file.name] = file.read_text(encoding="utf-8")
    return documents    

def retrieve(question):
    documents = load_documents()
    question = question.lower()
    for filename, content in documents.items():
        if question in content.lower():
            return filename, content
    return None, None