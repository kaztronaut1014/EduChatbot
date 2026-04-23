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
    
    # 1. Chuẩn hóa câu hỏi: Khôi phục ngữ cảnh + Viết tắt + Phân loại ý định
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
    
    # NGÃ RẼ 2 & 3: RAG VỚI NEO4J (TRA CỨU CHƯƠNG TRÌNH & CỔ CHAI)
    if clean_query.startswith("[CURRICULUM]") or clean_query.startswith("[BOTTLENECK]"):
        # Cắt bỏ cái Thẻ (Tag) để lấy đúng câu hỏi thật
        actual_query = clean_query.replace("[CURRICULUM]", "").replace("[BOTTLENECK]", "").strip()
        
        dynamic_examples = get_dynamic_examples(actual_query)
        dynamic_cypher_prompt = build_cypher_prompt(dynamic_examples)
        
        chain = GraphCypherQAChain.from_llm(
            cypher_llm=llm, qa_llm=llm, graph=graph,
            verbose=True, cypher_prompt=dynamic_cypher_prompt, 
            qa_prompt=qa_prompt, allow_dangerous_requests=True, top_k=200
        )
        
        try:
            # LẦN CHẠY 1: Thử chạy bình thường
            response = chain.invoke({"query": actual_query})
            final_answer = response["result"]
            
        except Exception as e:
            # BẮT BỆNH: Bắt lấy lỗi từ Neo4j
            error_msg = str(e)
            print(f"\n[⚠️] BẮT ĐƯỢC LỖI CYPHER: {error_msg}")
            print("[♻️] ĐANG KÍCH HOẠT TÍNH NĂNG TỰ SỬA LỖI (ZERO-SHOT REFLECTION)...")
            
            # SỬA SAI: Tạo câu lệnh bắt AI tự sửa
            reflection_query = (
                f"Câu hỏi gốc: {actual_query}\n\n"
                f"[SYSTEM ALERT]: Lần thử viết Cypher vừa rồi của bạn bị lỗi Syntax sau từ cơ sở dữ liệu Neo4j: '{error_msg}'. "
                f"Hãy đọc kỹ lại Schema, tự phân tích xem sai ở đâu (có thể do sai tên Node, thuộc tính hoặc cấu trúc MATCH) và viết một lệnh Cypher mới chuẩn xác hơn."
            )
            
            try:
                # LẦN CHẠY 2: Bắt nó chạy lại với thông tin lỗi đã đính kèm
                response_retry = chain.invoke({"query": reflection_query})
                final_answer = response_retry["result"]
                print("[✅] LLM ĐÃ TỰ SỬA LỖI!")
            except Exception as e2:
                # Nếu lần 2 vẫn ngu thì đành xin lỗi user
                print(f"[❌] SỬA LỖI THẤT BẠI: {str(e2)}")
                final_answer = "Dạ, hệ thống dữ liệu đang bị trục trặc một chút khi tìm môn này. Bạn thử hỏi lại theo cách khác hoặc kiểm tra lại tên môn giúp mình nhé! 😅"
        
        MEMORY_HISTORY.append(f"Sinh viên: {actual_query}\nBot: {final_answer}")
        return final_answer