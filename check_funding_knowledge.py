import chromadb

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Check if 'funding_knowledge' collection exists
existing_collections = client.list_collections()
if "funding_knowledge" not in existing_collections:
    print("❌ Error: 'funding_knowledge' collection does not exist!")
    exit()

# Retrieve stored funding knowledge
funding_collection = client.get_collection("funding_knowledge")
funding_data = funding_collection.get(include=["documents", "metadatas"])

# Display stored documents
docs = funding_data["documents"]
metadatas = funding_data["metadatas"]

if not docs:
    print("⚠️ No documents found in 'funding_knowledge'.")
else:
    print(f"\n📚 Stored Documents in 'funding_knowledge' ({len(docs)} entries):\n")
    for i, doc in enumerate(docs, 1):
        print(f"{i}. {doc[:200]}...")  # Print only first 200 chars to avoid clutter

print("\n✅ Done.")
