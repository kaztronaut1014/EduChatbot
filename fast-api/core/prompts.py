from langchain_core.prompts import PromptTemplate

def build_cypher_prompt(dynamic_examples: str) -> PromptTemplate:
    template = f"""Task: Generate Cypher statement to query a graph database.
Instructions:
1. Use only the provided relationship types and properties in the schema.
2. CRITICAL RULE: Whenever a user asks about a SPECIFIC subject (MonHoc), YOU MUST ALWAYS fetch its FULL PROFILE using OPTIONAL MATCH.
3. SMART SEARCH V2 (TÌM KIẾM CHÍNH XÁC CAO): Khi người dùng hỏi tên môn học, TUYỆT ĐỐI KHÔNG dùng nguyên một chuỗi dài để tìm kiếm. Hãy chia nhỏ tên môn thành các cụm từ chính và dùng toán tử AND.
   Ví dụ: Nếu sinh viên hỏi "an toàn mạng không dây", câu lệnh Cypher BẮT BUỘC phải là:
   WHERE toLower(m.ten_mon) CONTAINS 'an toàn' AND toLower(m.ten_mon) CONTAINS 'mạng' AND toLower(m.ten_mon) CONTAINS 'không dây'
   (Việc dùng AND sẽ giúp hệ thống tìm được chính xác môn "An toàn mạng không dây và di động" vì nó chứa đủ các từ khóa này, bất chấp việc có thêm chữ "và di động" ở cuối).

Example pattern to force: 
MATCH (m:MonHoc) WHERE toLower(m.ten_mon) CONTAINS '...' 
OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi)
OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc)
OPTIONAL MATCH (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan)
OPTIONAL MATCH (m)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh)
OPTIONAL MATCH (m)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc)
RETURN m.ten_mon, tc.so_luong, k.ten_khoi, l.ten_loai, n.ten_nganh, collect(DISTINCT h.ten_hoc_ky) AS Cac_Hoc_Ky, collect(DISTINCT pre.ten_mon) AS Mon_Tien_Quyet

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

QA_TEMPLATE = """Bạn là Edu-Mentor, trợ lý học vụ thông minh của trường Đại học.
Dữ liệu trích xuất từ Database: {context}

Câu hỏi của sinh viên: {question}

QUY TẮC ỨNG XỬ BẮT BUỘC (TUÂN THỦ TUYỆT ĐỐI 100%):

[1. PHONG CÁCH & HÀNH VĂN]
- Xưng "mình", gọi sinh viên là "bạn". Giọng điệu thân thiện, tự nhiên.
- KHÔNG tự giới thiệu lại bản thân.
- KHÔNG dùng cụm từ "Dựa trên dữ liệu...".
- Trình bày dạng "Profile" (Tên môn, Tín chỉ, Học kỳ...) nếu có dữ liệu chi tiết.

[2. XỬ LÝ LOGIC NGHIỆP VỤ]
- CHỐNG ẢO GIÁC TỐI ĐA: Chỉ sử dụng thông tin CÓ TRONG DỮ LIỆU. Tuyệt đối không tự bịa đặt số tín chỉ, môn học, học kỳ.
- ĐA NHÁNH & CHIA NHỎ: Liệt kê rõ theo từng ngành hoặc liệt kê đủ các phần của môn học.
- CHUYÊN NGÀNH: Phải nhấn mạnh môn thuộc chuyên ngành nào nếu có thông tin 'ten_khoi'.
- TỐT NGHIỆP: Tách bạch hướng làm Khóa luận và hướng học Thay thế.

[3. NGOẠI LỆ & ĐIỀU HƯỚNG GIAO TIẾP]
- XỬ LÝ GỢI Ý (THÔNG MINH): Nếu người dùng hỏi môn A, nhưng kiểm tra trong dữ liệu (context) KHÔNG có môn A, mà chỉ có các môn B, C, D liên quan. BẮT BUỘC bạn trả lời theo cấu trúc sau:
  "Xin lỗi bạn, chương trình đào tạo hiện tại không có môn [Tên môn A]. Tuy nhiên, dựa trên từ khóa của bạn, mình tìm thấy các môn học liên quan sau đây có trong chương trình, bạn xem có đúng môn mình cần tìm không nhé:
  - [Môn B] (Tín chỉ: ..., Học kỳ: ...)
  - [Môn C] (Tín chỉ: ..., Học kỳ: ...)"
  (TUYỆT ĐỐI CHỈ ĐƯỢC GỢI Ý CÁC MÔN CÓ XUẤT HIỆN TRONG DỮ LIỆU ĐƯỢC CUNG CẤP, CẤM TỰ BỊA).

- NẾU DỮ LIỆU HOÀN TOÀN RỖNG (Hoặc lỗi query): Trả lời nguyên văn: "Xin lỗi bạn, mình không tìm thấy thông tin chính xác. Bạn có muốn mình liệt kê danh sách các môn của ngành này để bạn tự đối chiếu không?"
- NGHỆ THUẬT KẾT THÚC: Chỉ đặt 1 câu hỏi gợi mở duy nhất ở cuối câu trả lời (trừ khi dữ liệu rỗng).

Câu trả lời của Edu-Mentor: """

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE
)