import chromadb

# Connect to ChromaDB
client = chromadb.PersistentClient(path="chroma_db")  # Adjust if necessary
collection = client.get_collection("knowledge_base")

# Retrieve all stored documents
results = collection.get(include=["documents"])  # Fetch stored documents

# Display the stored documents
print(f"\n📚 Stored Documents in 'knowledge_base' ({len(results['documents'])} entries):\n")
for i, doc in enumerate(results["documents"], 1):
    print(f"{i}. {doc}\n")
