import os
from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv

# Load các biến môi trường
load_dotenv()

def get_neo4j_graph():
    print("Đang kết nối Đồ thị Neo4j...")
    try:
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"), 
            username=os.getenv("NEO4J_USERNAME"), 
            password=os.getenv("NEO4J_PASSWORD"),
            database=os.getenv("NEO4J_USERNAME")
        )
        return graph
    except Exception as e:
        print(f"Lỗi kết nối Neo4j: {e}")
        return None