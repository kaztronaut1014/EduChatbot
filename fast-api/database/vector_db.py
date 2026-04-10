import chromadb

# Kết nối vào thư mục data đã tạo ở Bước 2
client = chromadb.PersistentClient(path="data/chromadb_data")
collection = client.get_collection(name="cypher_examples")

def get_dynamic_examples(query: str, n_results: int = 3) -> str:
    # Tìm n_results câu giống với query nhất
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    dynamic_examples_str = ""
    # Ráp các câu tìm được thành 1 chuỗi văn bản
    for i in range(len(results['documents'][0])):
        q = results['documents'][0][i]
        c = results['metadatas'][0][i]['cypher']
        dynamic_examples_str += f"Question: {q}\nCypher: {c}\n\n"
        
    return dynamic_examples_str