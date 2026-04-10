from langchain_core.prompts import PromptTemplate

CYPHER_GENERATION_TEMPLATE = """
Task: Generate Cypher statement to query a graph database.
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

Question: Môn Lập trình C# có bao nhiêu tín chỉ?
Cypher: MATCH (m:MonHoc {{ten_mon: 'Lập trình C#'}})-[:CO_SO_TIN_CHI]->(tc:TinChi) RETURN m.ten_mon, tc.so_luong

Question: Học kỳ 1 ngành Công nghệ thông tin học những môn gì?
Cypher: MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '1'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh {{ten_nganh: 'Công nghệ thông tin'}}) RETURN m.ten_mon, m.ma_hp

Question: Năm nhất ngành Công nghệ thông tin học những môn gì?
Cypher: MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS toLower('Công nghệ thông tin') AND h.ten_hoc_ky IN ['1', '2', '3'] RETURN m.ten_mon, h.ten_hoc_ky

Question: Năm 2 ngành Công nghệ thông tin học những môn gì?
Cypher: MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS toLower('Công nghệ thông tin') AND h.ten_hoc_ky IN ['4', '5', '6'] RETURN m.ten_mon, h.ten_hoc_ky

Question: Để học môn Đồ án tốt nghiệp ngành CNTT thì cần học môn nào trước?
Cypher: MATCH (m:MonHoc {{ten_mon: 'Đồ án tốt nghiệp'}})-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) RETURN pre.ten_mon, pre.ma_hp

Question: Kể tên các môn Chuyên ngành thuộc loại Tự chọn của ngành Quản lý giáo dục?
Cypher: MATCH (m:MonHoc)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc {{ten_khoi: 'Chuyên ngành'}}), (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan {{ten_loai: 'Tự chọn'}}), (m)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh {{ten_nganh: 'Quản lý giáo dục'}}) RETURN m.ten_mon

Question: {question}
Cypher: """

# CHÚ Ý: Đổi input_variables thành rỗng, vì GraphCypherQAChain tự xử lý biến bên dưới
CYPHER_PROMPT = PromptTemplate(
    input_variables=["question", "schema"], 
    template=CYPHER_GENERATION_TEMPLATE
)

QA_TEMPLATE = """Bạn là trợ lý học vụ Edu-Mentor.
Dữ liệu từ Database: {context}

Câu hỏi của sinh viên: {question}

Quy tắc trả lời:
1. KHÔNG tự giới thiệu lại bản thân ("mình là Edu-Mentor...", "Chào bạn...") vì bạn đã chào ở đầu phiên chat rồi.
2. Trả lời TRỰC TIẾP vào nội dung câu hỏi dựa trên dữ liệu được cung cấp.
3. Xưng hô "mình" và gọi sinh viên là "bạn". Thân thiện nhưng ngắn gọn.
4. Nếu dữ liệu (context) trống, hãy trả lời: "Xin lỗi bạn, mình chưa tìm thấy dữ liệu về câu hỏi này trong chương trình đào tạo."
5. Trình bày các ý bằng dấu gạch đầu dòng nếu có nhiều thông tin.
"""

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=QA_TEMPLATE
)