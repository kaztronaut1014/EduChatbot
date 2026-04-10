from fastapi import FastAPI
from core.bot_engine import ask_bot
import google.genai as genai

# Xem các model của Gemini (đã bỏ qua vì không cần thiết, chỉ cần dùng 1 model duy nhất là "gemini-3.1-flash-lite" để tối ưu chi phí)
# from dotenv import load_dotenv
# import os

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# for m in genai.list_models(): print(m.name)

app = FastAPI()

@app.get("/")
def home():
    return {"Message": "EduChatbot đã sẵn sàng nhận câu hỏi!"}

@app.get("/chat")
def chat_with_bot(q: str):
    try:
        # Gọi thẳng vào não bộ
        result = ask_bot(q)
        
        return {
            "Cau_Hoi": q,
            "Tra_Loi": result
        }
        
    except Exception as e:
        # Chuyển lỗi thành chữ thường để dễ tìm kiếm
        error_message = str(e).lower()
        
        # "Hết token / Hết request"
        if "429" in error_message or "quota" in error_message or "exhausted" in error_message:
            return {
                "Loi": "Hệ thống đang quá tải hoặc bot đã hết hạn mức trả lời trong ngày. Bạn vui lòng quay lại sau hoặc báo cho Admin nhé! 😭"
            }
            
        # Bắt các bệnh khác (lỗi code, lỗi db...)
        else:
            return {
                "Loi": f"Bot đang gặp sự cố kỹ thuật: {str(e)}"
            }