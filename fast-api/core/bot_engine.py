import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain
from core.prompts import CYPHER_PROMPT, qa_prompt
from database.neo4j_manager import get_neo4j_graph
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# 1. Khởi tạo Database
graph = get_neo4j_graph()

# 2. Khởi tạo LLM
print("Đang đánh thức Gemini...")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# 3. Tạo Chain ma thuật
chain = GraphCypherQAChain.from_llm(
    cypher_llm=llm,
    qa_llm=llm,
    graph=graph,
    verbose=True,
    cypher_prompt=CYPHER_PROMPT, 
    qa_prompt=qa_prompt,
    allow_dangerous_requests=True
)

# 4. Hàm giao tiếp chính để bên ngoài gọi vào
def ask_bot(query: str):
    response = chain.invoke({"query": query})
    return response["result"]