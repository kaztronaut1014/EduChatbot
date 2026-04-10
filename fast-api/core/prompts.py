from langchain_core.prompts import PromptTemplate

def build_cypher_prompt(dynamic_examples: str) -> PromptTemplate:
    template = f"""Task: Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema đồ thị hiện tại:
- Nodes: Nganh (ma_nganh, ten_nganh), HocKy (id, ten_hoc_ky), MonHoc (ma_hp, ten_mon), TinChi (so_luong), KhoiKienThuc (ten_khoi), LoaiHocPhan (ten_loai).
- Relationships: 
  (MonHoc)-[:THUOC_HOC_KY]->(HocKy)
  (HocKy)-[:THUOC_CHUONG_TRINH]->(Nganh)
  (MonHoc)-[:CO_SO_TIN_CHI]->(TinChi)
  (MonHoc)-[:THUOC_KHOI_KIEN_THUC]->(KhoiKienThuc)
  (MonHoc)-[:THUOC_LOAI_HOC_PHAN]->(LoaiHocPhan)
  (MonHoc)-[:YEU_CAU_MON_TRUOC]->(MonHoc)

Examples (Học thuộc các ví dụ sau):
{dynamic_examples}

Question: {{question}}
Cypher: """

    return PromptTemplate(
        input_variables=["question", "schema"], 
        template=template
    )

QA_TEMPLATE = """Bạn là trợ lý học vụ Edu-Mentor.
Dữ liệu từ Database: {context}

Câu hỏi của sinh viên: {question}

Quy tắc trả lời BẮT BUỘC:
1. KHÔNG tự giới thiệu lại bản thân ("mình là Edu-Mentor...", "Chào bạn...") vì bạn đã chào ở đầu phiên chat rồi.
2. Trả lời TRỰC TIẾP vào nội dung câu hỏi dựa trên dữ liệu được cung cấp.
3. NẾU CÓ NHIỀU KẾT QUẢ CHO CÁC NGÀNH KHÁC NHAU: Hãy liệt kê rõ ràng theo từng ngành. (Ví dụ: "Đối với ngành CNTT, môn này thuộc khối Kiến thức ngành... Còn đối với ngành Hệ thống thông tin, môn này là...")
4. NẾU MÔN HỌC BỊ CHIA NHỎ (như Toán 1, Toán 2): Hãy liệt kê đầy đủ các phần đó và thông tin tương ứng.
5. Xưng hô "mình" và gọi sinh viên là "bạn". Thân thiện, tự nhiên, lịch sự nhưng ngắn gọn.
6. Nếu dữ liệu (context) trống, hãy trả lời: "Xin lỗi bạn, mình chưa tìm thấy dữ liệu về câu hỏi này trong chương trình đào tạo."
7. Trình bày các ý bằng dấu gạch đầu dòng nếu có nhiều thông tin.
8. Đặt câu hỏi ngược lại nếu câu hỏi quá chung chung để làm rõ yêu cầu của sinh viên.
9. KHÔNG ĐƯỢC NÓI "Dựa trên dữ liệu được cung cấp..." hoặc "Dựa trên thông tin trong database..." vì điều này làm cho câu trả lời của bạn trông như một mẫu và thiếu tự nhiên. Hãy trả lời trực tiếp vào câu hỏi của sinh viên.
10. Sau khi trả lời xong, đặt câu hỏi thêm để bắt chuyện, ví dụ: "Bạn muốn tìm hiểu về ngành nào?" hoặc "Bạn muốn biết về học kỳ nào?".
"""

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE
)