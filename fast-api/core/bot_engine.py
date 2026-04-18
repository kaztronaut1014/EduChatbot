import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import GraphCypherQAChain
from core.prompts import build_cypher_prompt, qa_prompt, general_info_prompt
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

# Thêm import ở đầu file bot_engine.py
from core.prompts import general_info_prompt

def ask_bot(raw_query: str):
    print(f"\n[1] User gõ: {raw_query}")
    chat_history_str = get_history_string()
    
    # 1. Bác Lễ tân phân loại
    clean_query = normalize_student_query(raw_query, chat_history_str, llm)
    print(f"[2] Bot tự hiểu thành: {clean_query}")
    
    if clean_query == "OUT_OF_DOMAIN":
        reply = "Dạ, mình là trợ lý tư vấn giáo dục nên chỉ hỗ trợ các vấn đề về ngành học, môn học và hướng nghiệp thôi ạ 😊"
        MEMORY_HISTORY.append(f"User: {raw_query}\nBot: {reply}")
        return reply

    # NGÃ RẼ 1: HỎI THÔNG TIN CHUNG (REVIEW NGÀNH/CHUYÊN NGÀNH)
    if clean_query.startswith("[GENERAL_INFO]"):
        actual_query = clean_query.replace("[GENERAL_INFO]", "").strip()
        
        # Lấy template chém gió và gọi LLM trả lời trực tiếp (Bỏ qua RAG)
        prompt_val = general_info_prompt.format(question=actual_query)
        response = llm.invoke(prompt_val)
        
        # --- ĐOẠN FIX LỖI PARSING Ở ĐÂY ---
        if isinstance(response.content, list):
            final_answer = response.content[0].get("text", "") if len(response.content) > 0 else ""
        else:
            final_answer = str(response.content)
        # ----------------------------------
        
        MEMORY_HISTORY.append(f"Sinh viên: {actual_query}\nBot: {final_answer}")
        return final_answer
    
    # NGÃ RẼ 2: HỎI MÔN HỌC, TÍN CHỈ (ĐI VÀO GRAPH RAG NEO4J NHƯ CŨ)
    actual_query = clean_query.replace("[CURRICULUM]", "").strip()
    dynamic_examples = get_dynamic_examples(actual_query)
    dynamic_cypher_prompt = build_cypher_prompt(dynamic_examples)
    
    chain = GraphCypherQAChain.from_llm(
        cypher_llm=llm, qa_llm=llm, graph=graph,
        verbose=True, cypher_prompt=dynamic_cypher_prompt, 
        qa_prompt=qa_prompt, allow_dangerous_requests=True, top_k=200
    )
    
    response = chain.invoke({"query": actual_query})
    final_answer = response["result"]
    
    MEMORY_HISTORY.append(f"Sinh viên: {actual_query}\nBot: {final_answer}")
    return final_answer