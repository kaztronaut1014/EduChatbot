from langchain_core.prompts import PromptTemplate

# Từ điển viết tắt (Giữ nguyên của bạn)
ABBREVIATIONS = {
    "cntt": "Công nghệ thông tin",
    "ktpm": "Kỹ thuật phần mềm",
    "attt": "An toàn thông tin",
    "qlgd": "Quản lý giáo dục",
    "oop": "Lập trình hướng đối tượng",
    "csdl": "Cơ sở dữ liệu",
    "ctdl": "Cấu trúc dữ liệu và giải thuật",
    "cn": "Chuyên ngành",
    "tc": "Tự chọn",
    "bb": "Bắt buộc",
    "tín": "tín chỉ"
}

REWRITE_TEMPLATE = """Bạn là Lễ tân của hệ thống EduChatbot.
Lịch sử trò chuyện gần đây của sinh viên:
{history}

Câu hỏi mới của sinh viên: {query}

Nhiệm vụ của bạn thực hiện theo thứ tự sau:
1. KIỂM TRA CHỦ ĐỀ: Nếu câu hỏi mới KHÔNG liên quan đến trường học, đại học, môn học, tín chỉ, ngành học, lịch trình (ví dụ: rủ chơi game, hỏi đồ ăn, tán gẫu, hỏi thời tiết...), BẮT BUỘC bạn chỉ trả về dòng chữ: OUT_OF_DOMAIN
2. KHÔI PHỤC NGỮ CẢNH: Nếu câu hỏi hợp lệ nhưng có chứa các đại từ mập mờ (ví dụ: "môn đó", "học kỳ đó", "ngành này"), hãy dựa vào Lịch sử trò chuyện để điền đích danh tên môn/ngành vào câu hỏi mới.
3. CHUẨN HÓA VIẾT TẮT: Thay thế các từ lóng dựa vào từ điển sau:
{dict_context}

QUY TẮC SỐNG CÒN: 
- CHỈ trả về đúng 1 câu hỏi đã được viết lại, HOẶC trả về chữ OUT_OF_DOMAIN.
- Tuyệt đối KHÔNG giải thích, KHÔNG trả lời câu hỏi, KHÔNG dùng ngoặc kép.

Kết quả: """

rewrite_prompt = PromptTemplate(
    input_variables=["history", "query", "dict_context"],
    template=REWRITE_TEMPLATE
)

def normalize_student_query(raw_query: str, chat_history: str, llm) -> str:
    dict_str = "\n".join([f"- {k}: {v}" for k, v in ABBREVIATIONS.items()])
    
    # Ráp lịch sử và từ điển vào Prompt
    prompt_val = rewrite_prompt.format(
        history=chat_history if chat_history else "Chưa có", 
        query=raw_query, 
        dict_context=dict_str
    )
    
    response = llm.invoke(prompt_val)
    content = response.content
    
    if isinstance(content, list):
        text_result = content[0].get("text", "") if len(content) > 0 else ""
    else:
        text_result = str(content)
        
    return text_result.strip()