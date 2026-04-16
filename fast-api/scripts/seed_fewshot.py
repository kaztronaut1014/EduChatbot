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
    },
    {
        "id": "ex3",
        "question": "Để học môn Đồ án tốt nghiệp (hoặc môn X) thì cần học môn nào trước? Môn tiên quyết của môn này là gì?",
        "cypher": "MATCH (m:MonHoc)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc), (m)-[:THUOC_HOC_KY]->(:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(m.ten_mon) CONTAINS toLower('đồ án tốt nghiệp') RETURN m.ten_mon AS Mon_Hien_Tai, pre.ten_mon AS Mon_Tien_Quyet, n.ten_nganh"
    },
    {
        "id": "ex4",
        "question": "Môn Kỹ năng mềm (hoặc môn X) là môn bắt buộc hay tự chọn?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan), (m)-[:THUOC_HOC_KY]->(:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(m.ten_mon) CONTAINS toLower('kỹ năng mềm') RETURN m.ten_mon, l.ten_loai, n.ten_nganh"
    },
    {
        "id": "ex5",
        "question": "Kể tên các môn tự chọn của ngành Công nghệ thông tin (hoặc ngành Y)?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_LOAI_HOC_PHAN]->(l:LoaiHocPhan {{ten_loai: 'Tự chọn'}}), (m)-[:THUOC_HOC_KY]->(:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS toLower('công nghệ thông tin') RETURN m.ten_mon, m.ma_hp"
    },
    {
        "id": "ex6",
        "question": "Học kỳ 1 ngành Quản lý giáo dục (hoặc ngành Z) có tổng cộng bao nhiêu tín chỉ? Học kỳ này học những môn gì?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '1'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS toLower('quản lý giáo dục') OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) RETURN n.ten_nganh, h.ten_hoc_ky, m.ten_mon, tc.so_luong, k.ten_khoi"
    },
    {
        "id": "ex7",
        "question": "Khối kiến thức đại cương của ngành Công nghệ thông tin gồm những môn nào?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc), (m)-[:THUOC_HOC_KY]->(:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(k.ten_khoi) CONTAINS toLower('đại cương') AND toLower(n.ten_nganh) CONTAINS toLower('công nghệ thông tin') RETURN m.ten_mon, k.ten_khoi, n.ten_nganh"
    },
    # --- XỬ LÝ TỐT NGHIỆP (Khóa luận vs Học phần thay thế) ---
    {
        "id": "ex8",
        "question": "Điều kiện tốt nghiệp ngành Công nghệ thông tin là gì? (hoặc làm sao để tốt nghiệp, có những môn nào để xét tốt nghiệp?)",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc), (m)-[:THUOC_HOC_KY]->(:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS toLower('công nghệ thông tin') AND (toLower(k.ten_khoi) CONTAINS toLower('khóa luận') OR toLower(k.ten_khoi) CONTAINS toLower('thay thế')) RETURN m.ten_mon, k.ten_khoi, n.ten_nganh"
    },
    
    # --- XỬ LÝ NHIỀU HỌC KỲ VÀ TRUY VẤN CHUYÊN NGÀNH CỦA 1 MÔN ---
    # Chú ý: Dùng collect(h.ten_hoc_ky) để gom tất cả học kỳ thành 1 mảng nếu môn đó dạy ở nhiều kỳ
    {
        "id": "ex9",
        "question": "Môn Khai thác dữ liệu (hoặc môn X) học ở học kỳ mấy? Môn này thuộc chuyên ngành nào?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh), (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) WHERE toLower(m.ten_mon) CONTAINS toLower('khai thác dữ liệu') RETURN m.ten_mon, n.ten_nganh, k.ten_khoi, collect(h.ten_hoc_ky) AS Cac_Hoc_Ky"
    },

    # --- XỬ LÝ LIỆT KÊ MÔN TRONG 1 CHUYÊN NGÀNH CỤ THỂ ---
    {
        "id": "ex10",
        "question": "Chuyên ngành Kỹ thuật phần mềm (hoặc chuyên ngành X) gồm những môn nào?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc), (m)-[:THUOC_HOC_KY]->(h:HocKy)-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(k.ten_khoi) CONTAINS toLower('chuyên ngành kỹ thuật phần mềm') RETURN m.ten_mon, h.ten_hoc_ky, n.ten_nganh, k.ten_khoi"
    },
    # --- XỬ LÝ LIỆT KÊ MÔN HỌC THEO HỌC KỲ (BẮT BUỘC LẤY KHỐI KIẾN THỨC VÀ HỌC KỲ) ---
    {
        "id": "ex11",
        "question": "Học kỳ 2 ngành Công nghệ thông tin học những môn gì? Cần học những môn nào trước?",
        "cypher": "MATCH (m:MonHoc)-[:THUOC_HOC_KY]->(h:HocKy {{ten_hoc_ky: '2'}})-[:THUOC_CHUONG_TRINH]->(n:Nganh) WHERE toLower(n.ten_nganh) CONTAINS 'công nghệ thông tin' OPTIONAL MATCH (m)-[:THUOC_KHOI_KIEN_THUC]->(k:KhoiKienThuc) OPTIONAL MATCH (m)-[:YEU_CAU_MON_TRUOC]->(pre:MonHoc) OPTIONAL MATCH (m)-[:CO_SO_TIN_CHI]->(tc:TinChi) RETURN m.ten_mon, k.ten_khoi, tc.so_luong, collect(DISTINCT pre.ten_mon) AS Mon_Tien_Quyet"
    }

]

# Chuẩn bị dữ liệu
documents = [ex["question"] for ex in examples]
metadatas = [{"cypher": ex["cypher"]} for ex in examples]
ids = [ex["id"] for ex in examples]

# Đẩy vào database
collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
print(f"✅ Đã nạp thành công {len(examples)} ví dụ vào ChromaDB!")