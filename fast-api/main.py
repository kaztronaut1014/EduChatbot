from fastapi import FastAPI
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()

# ================= 1. KẾT NỐI NÃO BỘ LƯU TRỮ (NEO4J) =================
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# ================= 2. KẾT NỐI NÃO BỘ TƯ DUY (GEMINI) =================
# DÁN API KEY GEMINI CỦA ÔNG VÀO ĐÂY (Lấy từ Google AI Studio)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# ================= 2. KẾT NỐI NÃO BỘ =================
print("Đang kết nối Đồ thị Neo4j...")
graph = Neo4jGraph(
    url=URI, 
    username=USER, 
    password=PASSWORD,
    database=USER
)

print("Đang đánh thức Gemini...")
# Dùng bản gemini-2.5-flash như ông báo lúc nãy, temperature=0 để nó trả lời chính xác, bớt chém gió
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

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

Question: Để học môn Đồ án tốt nghiệp ngành CNTT thì cần học môn nào trước?
Cypher: MATCH (m:MonHoc {{ten_mon: 'Đồ án tốt nghiệp'}})-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) RETURN pre.ten_mon, pre.ma_hp

Question: Kể tên các môn Chuyên ngành thuộc loại Tự chọn của ngành Quản lý giáo dục?
Cypher: MATCH (m:MonHoc)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc {{ten_khoi: 'Chuyên ngành'}}), (m)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan {{ten_loai: 'Tự chọn'}}), (m)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh {{ten_nganh: 'Quản lý giáo dục'}}) RETURN m.ten_mon

Question: {question}
Cypher: """

CYPHER_PROMPT = PromptTemplate(
    input_variables=["question"], 
    template=CYPHER_GENERATION_TEMPLATE
)

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""Bạn là Edu-Mentor, một trợ lý học vụ thông minh của trường Đại học.
Bạn đang tư vấn cho sinh viên tân sinh viên.
Dựa vào dữ liệu được cung cấp từ Database: {context}
Hãy trả lời câu hỏi: {question}
Quy tắc:
- Xưng hô "mình" và gọi sinh viên là "bạn".
- Trả lời thân thiện, tự nhiên, dễ hiểu, trình bày rõ ràng.
- Nếu dữ liệu (context) trống, hãy nói: "Xin lỗi bạn, mình chưa tìm thấy dữ liệu về câu hỏi này trong chương trình đào tạo hiện tại."
"""
)

# Tạo "Cầu nối" ma thuật: Text -> Cypher -> Neo4j -> Text
chain = GraphCypherQAChain.from_llm(
    cypher_llm=llm,             # Dùng Gemini để dịch tiếng Việt sang Cypher
    qa_llm=llm,                 # Dùng Gemini để lấy dữ liệu Cypher viết thành câu trả lời    
    graph=graph,
    verbose=True,               # In log ra terminal để debug
    cypher_prompt=CYPHER_PROMPT, 
    qa_prompt=qa_prompt,
    allow_dangerous_requests=True # Cấp quyền cho AI đọc Database
)

# ================= 3. API ĐỂ CHAT =================
@app.get("/")
def home():
    return {"Message": "EduChatbot đã sẵn sàng nhận câu hỏi!"}

# API nhận câu hỏi từ trình duyệt
@app.get("/chat")
def chat_with_bot(q: str):
    try:
        
        # AI bắt đầu suy nghĩ và lục data
        response = chain.invoke({"query": q})
        
        return {
            "Cau_Hoi": q,
            "Tra_Loi": response["result"]
        }
    except Exception as e:
        return {"Loi": f"Bot đang bị lú: {str(e)}"}
    
