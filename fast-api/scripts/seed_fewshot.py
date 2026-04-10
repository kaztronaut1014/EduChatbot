import chromadb
import os

# Tạo thư mục chứa database vector nếu chưa có
os.makedirs("data/chromadb_data", exist_ok=True)

# Khởi tạo ChromaDB
client = chromadb.PersistentClient(path="data/chromadb_data")
collection = client.get_or_create_collection(name="cypher_examples")

# Danh sách các ví dụ mẫu (bạn có thể thêm 50-100 câu vào đây sau)
examples = [
    {
        "id": "ex1",
        "question": "Môn Lập trình hướng đối tượng (hoặc oop) có bao nhiêu tín chỉ và thuộc khối nào?",
        "cypher": "MATCH (m:MonHoc)-[:CO_SO_TIN_CHI]->(tc:TinChi), (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc), (m)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(m.ten_mon) CONTAINS toLower('lập trình hướng đối tượng') RETURN m.ten_mon, tc.so_luong, k.ten_khoi, n.ten_nganh"
    },
    {
        "id": "ex2",
        "question": "Môn Toán cao cấp (có thể chia làm 1, 2, 3) học ở học kỳ mấy?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(m.ten_mon) CONTAINS toLower('toán cao cấp') RETURN m.ten_mon, h.ten_hoc_ky, n.ten_nganh"
    }
]

# Chuẩn bị dữ liệu
documents = [ex["question"] for ex in examples]
metadatas = [{"cypher": ex["cypher"]} for ex in examples]
ids = [ex["id"] for ex in examples]

# Đẩy vào database
collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
print(f"✅ Đã nạp thành công {len(examples)} ví dụ vào ChromaDB!")