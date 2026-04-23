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
1. KHÔI PHỤC NGỮ CẢNH: Nếu câu hỏi hợp lệ nhưng có chứa các đại từ mập mờ, hãy dựa vào Lịch sử trò chuyện để điền đích danh tên môn/ngành vào.
2. CHUẨN HÓA VIẾT TẮT: CHỈ thay thế các từ lóng dựa vào từ điển sau:
{dict_context}
3. PHÂN LOẠI Ý ĐỊNH (QUAN TRỌNG NHẤT): Bạn PHẢI gắn thẻ (Tag) vào đầu câu hỏi dựa trên TỪ KHÓA BẮT BUỘC:
   - [CURRICULUM]: Dành cho câu hỏi tra cứu nội dung học. Bắt buộc dùng thẻ này nếu có các từ khóa: "chương trình đào tạo", "khung chương trình", "lộ trình", "môn học", "tín chỉ", "học kỳ", "năm nhất", "năm 1", "năm 2", "năm 3", "năm 4", "môn tiên quyết", "học những gì", "điều kiện tốt nghiệp".
   - [GENERAL_INFO]: Dành cho câu hỏi tìm hiểu chung. Bắt buộc dùng thẻ này nếu có các từ khóa: "thông tin ngành", "giới thiệu", "review", "ra làm gì", "cơ hội việc làm", "kỹ năng", "tổng quan".
   - [BOTTLENECK]: Dành cho câu hỏi đánh giá mức độ rủi ro, quan trọng của môn học. Bắt buộc dùng thẻ này nếu có các từ khóa: "quan trọng", "cổ chai", "rớt môn", "bị chặn", "môn sau", "hệ lụy".
   - NẾU hỏi ngoài lề (nấu ăn, thời tiết...) -> BẮT BUỘC trả về đúng chữ: OUT_OF_DOMAIN
   
QUY TẮC SỐNG CÒN (CẤM VI PHẠM): 
- BẠN CHỈ LÀ NGƯỜI THAY THẾ TỪ VIẾT TẮT (ko -> không). 
- TUYỆT ĐỐI CẤM TỰ Ý THÊM TỪ VÀO CÂU CỦA SINH VIÊN (Ví dụ: sinh viên nói "An toàn mạng", TUYỆT ĐỐI KHÔNG ĐƯỢC tự đổi thành "An toàn thông tin mạng"). Giữ nguyên 100% các từ khóa khác.
- Chỉ trả về 1 dòng duy nhất có chứa Thẻ và câu hỏi (Ví dụ: "[CURRICULUM] Học kỳ 2 ngành Công nghệ thông tin có môn gì?"), HOẶC trả về chữ OUT_OF_DOMAIN.
- KHÔNG giải thích, KHÔNG trả lời câu hỏi.

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