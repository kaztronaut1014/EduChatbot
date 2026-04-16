import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain
from core.prompts import build_cypher_prompt, qa_prompt
from database.neo4j_manager import get_neo4j_graph
from database.vector_db import get_dynamic_examples
from core.normalizer import normalize_student_query 
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

graph = get_neo4j_graph()
llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", temperature=0)

# === TẠO BỘ NHỚ TẠM THỜI ===
# Trong thực tế đồ án, bạn có thể lưu cái này vào Database hoặc Session của Frontend.
# Để test nhanh, ta dùng 1 mảng lưu tạm trên server.
MEMORY_HISTORY = []

def get_history_string():
    """Chuyển mảng lịch sử thành chuỗi để LLM đọc"""
    # Chỉ lấy 4 tin nhắn gần nhất để khỏi tràn token
    recent_history = MEMORY_HISTORY[-4:] 
    return "\n".join(recent_history)

def ask_bot(raw_query: str):
    print(f"\n[1] User gõ: {raw_query}")
    
    # Lấy lịch sử ném cho bác Phiên dịch
    chat_history_str = get_history_string()
    
    # 1. Bác Lễ tân / Phiên dịch làm việc
    clean_query = normalize_student_query(raw_query, chat_history_str, llm)
    print(f"[2] Bot tự hiểu thành: {clean_query}")
    
    # 2. XỬ LÝ GUARDRAILS (Từ chối khéo)
    if clean_query == "OUT_OF_DOMAIN":
        reply = "Dạ, mình là trợ lý học vụ Edu-Mentor nên chỉ được phép hỗ trợ các vấn đề về chương trình đào tạo, môn học và tín chỉ thôi ạ. Bạn có câu hỏi nào về việc học không? 😊"
        # Lưu câu hỏi rác này vào bộ nhớ để bot biết user vừa đùa dai
        MEMORY_HISTORY.append(f"Sinh viên: {raw_query}")
        MEMORY_HISTORY.append(f"Bot: {reply}")
        return reply

    # 3. Luồng RAG bình thường (nếu câu hỏi hợp lệ)
    dynamic_examples = get_dynamic_examples(clean_query)
    dynamic_cypher_prompt = build_cypher_prompt(dynamic_examples)
    
    chain = GraphCypherQAChain.from_llm(
        cypher_llm=llm,
        qa_llm=llm,
        graph=graph,
        verbose=True,
        cypher_prompt=dynamic_cypher_prompt, 
        qa_prompt=qa_prompt,
        allow_dangerous_requests=True,
        top_k=100
    )
    
    response = chain.invoke({"query": clean_query})
    final_answer = response["result"]
    
    # 4. Lưu lại lịch sử sau khi trả lời thành công
    MEMORY_HISTORY.append(f"Sinh viên: {clean_query}") # Lưu câu đã làm sạch cho dễ hiểu
    MEMORY_HISTORY.append(f"Bot: {final_answer}")
    
    return final_answer