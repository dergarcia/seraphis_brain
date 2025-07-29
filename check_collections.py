import chromadb

client = chromadb.PersistentClient(path="chroma_db")  # Adjust path if needed

collections = client.list_collections()

if collections:
    print("Existing collections in ChromaDB:")
    for col in collections:
        print("-", col)  # Directly print the collection name
else:
    print("No collections found in ChromaDB.")


